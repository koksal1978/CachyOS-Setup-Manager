#!/usr/bin/env python3
import json, os, sys, subprocess, shutil, datetime, pathlib, shlex
from PySide6.QtCore import QThread, Signal, Qt, QSize
from PySide6.QtGui import QIcon, QColor, QBrush, QFont, QPixmap, QPainter
from PySide6.QtWidgets import QListWidget, QComboBox, QHeaderView, QFrame, QTabWidget, QAbstractItemView
from PySide6.QtWidgets import (QApplication,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QTreeWidget,QTreeWidgetItem,QPlainTextEdit,QProgressBar,QCheckBox,QMessageBox,QLineEdit,QInputDialog)
ROOT=pathlib.Path(__file__).resolve().parent
CAT=json.loads((ROOT/'catalog.json').read_text())
META=json.loads((ROOT/'metadata.json').read_text())
STATE=pathlib.Path.home()/'.local/state/cachyos-setup-manager'
STATE.mkdir(mode=0o700,parents=True,exist_ok=True)
def runcheck(args):
    try: return subprocess.run(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
    except OSError: return False
EXTRAS={2:[('dbeaver-java','DBeaver: kalıcı Java 21')],6:[('docker-service','Docker servisini etkinleştir'),('portainer','Portainer (localhost:9443)'),('mssql','SQL Server 2022 Developer (localhost:1433)')],7:[('libvirt','Libvirt ve varsayılan NAT ağı')],8:[('duplicati','Duplicati kullanıcı servisi')],9:[('opensnitch','OpenSnitch servisi')],10:[('shortcuts','Bilgisayarım, Portainer, Duplicati kısayolları')],0:[('numlock','Oturum NumLock ayarı')],1:[('flatpak','Flatpak uygulamaları')]}
MANUAL={0:'Disk bağlantıları, Plasma Login, güvenlik duvarı ve boot ayarları',3:'IDE hesapları, SDK ve geliştirme araçlarına özel ayarlar',4:'Wine önekleri, Windows uygulamaları ve eski Java uygulamaları',5:'VPN profilleri ve kimlik bilgileri',7:'Sanal disk dönüşümü, Ethernet köprüsü, SPICE ve RDP rehberi',8:'Yedek arşivleri ve geri yükleme testi'}
class UpdateScan(QThread):
    result=Signal(dict,str)
    def run(self):
        updates={}; notes=[]
        for label,args in [('Depo',['checkupdates']),('AUR',['paru','-Qua'])]:
            if not shutil.which(args[0]):notes.append(label+': araç yok');continue
            try:
                r=subprocess.run(args,capture_output=True,text=True,timeout=180)
                if r.returncode not in (0,2):notes.append(label+': kontrol başarısız');continue
                for line in r.stdout.splitlines():
                    parts=line.split()
                    if len(parts)==4 and parts[2]=='->':updates[parts[0]]=parts[3]
                notes.append(label+': kontrol tamamlandı')
            except Exception as e:notes.append(label+': '+str(e))
        self.result.emit(updates,' | '.join(notes))
class Worker(QThread):
    log=Signal(str); progress=Signal(int); done=Signal(int,int)
    def __init__(self,items,apply,aur,password,update):
        super().__init__(); self.items=items; self.apply=apply; self.aur=aur; self.password=password; self.update=update
    def cmd(self,args,secret_env=None):
        self.log.emit('$ '+shlex.join(args)); env=os.environ.copy(); env.update(secret_env or {})
        if not self.apply:return True
        try:
            p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',stdin=subprocess.DEVNULL,env=env)
            for line in p.stdout:self.log.emit(line.rstrip().replace(self.password,'[GİZLİ]') if self.password else line.rstrip())
            ok=p.wait()==0
            if not ok:
                self.log.emit('Güncelleme veya kurulum başarısızsa: Güncelleme hataları / çözüm bölümünü inceleyin. Dosyaları otomatik silmeyin.')
            return ok
        except OSError as e:self.log.emit(str(e));return False
    def extra(self,k):
        commands={
         'docker-service':[['sudo','-n','systemctl','enable','--now','docker']],
         'duplicati':[['systemctl','--user','enable','--now','duplicati.service']],
         'opensnitch':[['sudo','-n','systemctl','enable','--now','opensnitchd']],
         'libvirt':[['sudo','-n','systemctl','enable','--now','libvirtd'],['sudo','-n','usermod','-aG','libvirt,kvm',__import__('pwd').getpwuid(os.getuid()).pw_name],['sudo','-n','virsh','net-autostart','default']],
         'numlock':[['kwriteconfig6','--file','kcminputrc','--group','Keyboard','--key','NumLock','0']],
         'flatpak':[['sudo','-n','flatpak','remote-add','--if-not-exists','flathub','https://flathub.org/repo/flathub.flatpakrepo'],['sudo','-n','flatpak','install','-y','--noninteractive','flathub','io.missioncenter.MissionCenter','net.davidotek.pupgui2','com.devolutions.remotedesktopmanager']],
        }
        if k in commands:
            ok=all(self.cmd(c) for c in commands[k]);
            if k=='libvirt' and ok:
                if self.apply and runcheck(['sudo','-n','virsh','net-info','default']):
                    active=subprocess.run(['sudo','-n','virsh','net-list','--name'],capture_output=True,text=True).stdout.splitlines()
                    if 'default' not in active:ok=self.cmd(['sudo','-n','virsh','net-start','default'])
            return ok
        if k in ('portainer','mssql'):
            name='portainer' if k=='portainer' else 'mssql2022'; volume='portainer_data' if k=='portainer' else 'mssql2022_data'
            if runcheck(['sudo','-n','docker','container','inspect',name]):
                self.log.emit(name+' mevcut; yapılandırma korunuyor.');return self.cmd(['sudo','-n','docker','start',name])
            if k=='mssql' and not self.password:self.log.emit('SQL şifresi girilmedi; atlandı.');return False
            if not self.cmd(['sudo','-n','docker','volume','create',volume]):return False
            args=['sudo','-n','docker','run','-d','--name',name,'--restart','unless-stopped']
            if k=='portainer':return self.cmd(args+['-p','127.0.0.1:9443:9443','-v','/var/run/docker.sock:/var/run/docker.sock','-v',volume+':/data','portainer/portainer-ce:lts'])
            return self.cmd(['sudo','-n','--preserve-env=MSSQL_SA_PASSWORD']+args[2:]+['-p','127.0.0.1:1433:1433','-v',volume+':/var/opt/mssql','-e','ACCEPT_EULA=Y','-e','MSSQL_PID=Developer','-e','MSSQL_SA_PASSWORD','mcr.microsoft.com/mssql/server:2022-latest'],{'MSSQL_SA_PASSWORD':self.password})
        if k=='dbeaver-java':
            path=pathlib.Path('/usr/lib/dbeaver/dbeaver.ini'); self.log.emit('DBeaver Java 21: '+str(path))
            if not self.apply:return True
            if not path.is_file() or not pathlib.Path('/usr/lib/jvm/java-21-openjdk/bin/java').is_file():return False
            lines=path.read_text().splitlines(); i=0; new=[]
            while i<len(lines):
                if lines[i]=='-vm':i+=2;continue
                new.append(lines[i]);i+=1
            if '-vmargs' not in new:return False
            i=new.index('-vmargs');new[i:i]=['-vm','/usr/lib/jvm/java-21-openjdk/bin/java']
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w',delete=False) as f:f.write('\n'.join(new)+'\n');tmp=f.name
            try:return self.cmd(['sudo','-n','cp','--no-clobber',str(path),str(path)+'.setup-bak']) and self.cmd(['sudo','-n','install','-m','644',tmp,str(path.resolve())])
            finally:os.unlink(tmp)
        if k=='shortcuts':
            if not self.apply:self.log.emit('Yerel .desktop dosyaları oluşturulacak.');return True
            desktop=subprocess.run(['xdg-user-dir','DESKTOP'],capture_output=True,text=True).stdout.strip(); dirs=[pathlib.Path.home()/'.local/share/applications'];
            if desktop and pathlib.Path(desktop).is_dir():dirs.append(pathlib.Path(desktop))
            for name,exe,icon in [('Bilgisayarım','nemo computer:///','computer'),('Portainer','xdg-open https://localhost:9443','applications-system'),('Duplicati','xdg-open http://localhost:8200','document-save')]:
                for d in dirs:
                    d.mkdir(parents=True,exist_ok=True);p=d/(name+'.desktop')
                    if not p.exists():p.write_text(f'[Desktop Entry]\nType=Application\nName={name}\nExec={exe}\nIcon={icon}\nTerminal=false\n');p.chmod(0o755)
            return True
        return False
    def run(self):
        good=bad=0
        try:
            if self.apply and not self.cmd(['sudo','-n','true']):self.log.emit('Önce terminalde sudo -v çalıştırın.');self.done.emit(0,len(self.items));return
            if self.update and not self.cmd(['sudo','-n','pacman','-Syu','--noconfirm']):self.done.emit(0,len(self.items));return
            for i,(kind,k) in enumerate(self.items):
                try:
                    if kind=='system-update':
                        ok=True if self.update else self.cmd(['sudo','-n','pacman','-Syu','--noconfirm'])
                        if ok and self.aur and shutil.which('paru'):ok=self.cmd(['paru','-Sua','--noconfirm'])
                        if ok and shutil.which('flatpak'):ok=self.cmd(['sudo','-n','flatpak','update','--system','-y','--noninteractive'])
                    elif kind=='package':
                        if runcheck(['pacman','-Q',k]):self.log.emit(k+' — zaten kurulu');ok=True
                        elif runcheck(['pacman','-Si',k]):ok=self.cmd(['sudo','-n','pacman','-S','--needed','--noconfirm',k])
                        elif self.aur and shutil.which('paru'):ok=self.cmd(['paru','-S','--needed','--noconfirm',k])
                        else:self.log.emit(k+' — depoda yok, AUR/elle inceleme gerekli');ok=False
                        if self.apply and ok:ok=runcheck(['pacman','-Q',k])
                    else:ok=self.extra(k)
                except Exception as e:self.log.emit(str(e));ok=False
                if ok:good+=1
                else:bad+=1
                self.log.emit(('OK: ' if ok else 'BAŞARISIZ/ATLANDI: ')+k);self.progress.emit(int((i+1)*100/len(self.items)))
            self.done.emit(good,bad)
        finally:self.password=''
EXTRA_DESC={
'dbeaver-java':'DBeaver açılış hatasını giderir; Java 8 varsayılanını değiştirmez.',
'docker-service':'Docker servisini başlatır ve açılışta etkinleştirir.',
'portainer':'Docker için web yönetim paneli; yerel 9443 portu.',
'mssql':'Yerel SQL Server 2022 Developer; kalıcı veri alanı ve 1433 portu.',
'libvirt':'KVM servisi, kullanıcı grupları ve NAT sanal ağı.',
'duplicati':'Kullanıcı yedekleme servisini başlatır.',
'opensnitch':'Uygulama ağ denetimi servisini etkinleştirir.',
'shortcuts':'Nemo Bilgisayarım, Portainer ve Duplicati kısayolları.',
'numlock':'KDE oturumunda NumLock ayarını etkinleştirir.',
'flatpak':'Remote Desktop Manager, Mission Center ve ProtonUp-Qt kurulumu.'}
ICON_ALIASES={'visual-studio-code-bin':['visual-studio-code','code'],'google-chrome':['google-chrome'],'azuredatastudio-bin':['azuredatastudio'],'onlyoffice-bin':['onlyoffice-desktopeditors'],'postman-bin':['postman'],'duplicati-bin':['duplicati'],'zen-browser-bin':['zen-browser','zen'],'flutter-bin':['flutter'],'powershell-bin':['powershell','pwsh'],'ventoy-bin':['ventoy'],'wireshark-qt':['wireshark'],'zint-qt':['zint'],'mission-center':['io.missioncenter.MissionCenter','mission-center'],'docker-service':['docker'],'mssql':['server-database'],'dbeaver-java':['dbeaver'],'portainer':['portainer']}
ICON_CACHE={}
def app_icon(key,name):
    if key in ICON_CACHE:return ICON_CACHE[key]
    aliases=ICON_ALIASES.get(key,[])+[key,key.removesuffix('-bin'),key.removesuffix('-qt')]
    for alias in aliases:
        icon=QIcon.fromTheme(alias)
        if not icon.isNull():ICON_CACHE[key]=icon;return icon
    # Read package-owned launcher icon names when the application is installed.
    if key in META and shutil.which('pacman'):
        try:
            import configparser
            r=subprocess.run(['pacman','-Qlq',key],capture_output=True,text=True,timeout=3)
            for f in r.stdout.splitlines():
                if '/applications/' not in f or not f.endswith('.desktop'):continue
                cfg=configparser.ConfigParser(interpolation=None,strict=False);cfg.read(f,encoding='utf-8');v=cfg.get('Desktop Entry','Icon',fallback='')
                icon=QIcon(v) if v.startswith('/') else QIcon.fromTheme(v)
                if not icon.isNull():ICON_CACHE[key]=icon;return icon
        except Exception:pass
    # Clearly generic monogram, not a simulated official logo.
    pix=QPixmap(40,40);pix.fill(QColor('#e5edf8'));p=QPainter(pix);p.setPen(QColor('#325477'));p.setFont(QFont('Sans Serif',12,QFont.Weight.Bold));p.drawText(pix.rect(),Qt.AlignmentFlag.AlignCenter,name[:2].upper());p.end();icon=QIcon(pix);ICON_CACHE[key]=icon;return icon
class Window(QWidget):
    def __init__(self):
        super().__init__();self.setWindowTitle('CachyOS Setup Manager 0.8 Public');self.resize(1280,820);self.setMinimumSize(880,650)
        layout=QVBoxLayout(self);layout.setContentsMargins(18,16,18,16);layout.setSpacing(10)
        self.setStyleSheet("""
        QWidget {font-size: 13px;} QLabel#heading {font-size:24px;font-weight:700;}
        QLabel#sub {font-size:13px;color:palette(mid);}
        QPushButton {padding:8px 12px; border:1px solid palette(midlight);border-radius:7px;}
        QPushButton:hover {border-color:#5794dc;} QPushButton#primary {background:#2563a8;color:white;font-weight:600;border:0;}
        QPushButton#primary:disabled {background:#8898ac;} QLineEdit,QComboBox {padding:8px;border:1px solid palette(midlight);border-radius:7px;}
        QListWidget,QTreeWidget,QPlainTextEdit {border:1px solid palette(midlight);border-radius:8px;}
        QTreeWidget::item {padding:5px;} QHeaderView::section {padding:8px;border:0;border-bottom:1px solid palette(midlight);font-weight:600;}
        """)
        heading=QLabel('CachyOS Setup Manager');heading.setObjectName('heading');layout.addWidget(heading)
        sub=QLabel('Uygulama merkezi  •  11 kategori  •  Genel paket kataloğu');layout.addWidget(sub)
        tools=QHBoxLayout();layout.addLayout(tools);self.search=QLineEdit();self.search.setPlaceholderText('Uygulama adı, paket kodu veya açıklama ara…');tools.addWidget(self.search,3)
        self.statusfilter=QComboBox();self.statusfilter.addItems(['Tüm durumlar','Kurulu','Kurulu değil','Güncelleme var','Yapılandırma / manuel']);tools.addWidget(self.statusfilter,1)
        self.scanbutton=QPushButton('Güncelleme kontrolü');self.scanbutton.clicked.connect(self.scan_updates);tools.addWidget(self.scanbutton)
        body=QHBoxLayout();layout.addLayout(body,1)
        left=QVBoxLayout();body.addLayout(left);self.categories=QListWidget();self.categories.setFixedWidth(230);self.categories.addItem('Tüm uygulamalar')
        for g in CAT:self.categories.addItem(g['name'])
        self.categories.setWordWrap(True);self.categories.setSpacing(4);self.categories.setCurrentRow(0);left.addWidget(self.categories,1)
        guide=QPushButton('Genel kurulum rehberi');guide.clicked.connect(lambda:subprocess.Popen(['xdg-open',str(ROOT/'rehber.html')]));left.addWidget(guide)
        repair=QPushButton('Güncelleme hataları / çözüm');repair.clicked.connect(lambda:subprocess.Popen(['xdg-open',(ROOT/'rehber.html').as_uri()+'#update-conflicts']));left.addWidget(repair)
        from vmtools import DiskDialog, BridgeDialog
        disk=QPushButton('Sanal disk dönüştür');disk.clicked.connect(lambda:DiskDialog(self).exec());left.addWidget(disk)
        bridge=QPushButton('Ethernet köprüsü / br0');bridge.clicked.connect(lambda:BridgeDialog(self).exec());left.addWidget(bridge)
        vmguide=QPushButton('KVM / SPICE / RDP rehberi');vmguide.clicked.connect(lambda:subprocess.Popen(['xdg-open',(ROOT/'rehber.html').as_uri()+'#vm-migration']));left.addWidget(vmguide)
        right=QVBoxLayout();body.addLayout(right,1)
        self.summary=QLabel();right.addWidget(self.summary)
        self.tree=QTreeWidget();self.tree.setHeaderLabels(['Uygulama / paket','Ne işe yarar?','Durum','Kurulu sürüm','Yeni sürüm']);self.tree.setIconSize(QSize(34,34));self.tree.setAlternatingRowColors(True);self.tree.setRootIsDecorated(False);self.tree.setWordWrap(True);self.tree.setIndentation(12);right.addWidget(self.tree,1)
        self.tree.header().setSectionResizeMode(0,QHeaderView.ResizeMode.Interactive);self.tree.header().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        for i,w in [(0,260),(2,132),(3,125),(4,105)]:self.tree.setColumnWidth(i,w)
        self.installed=set();self.versions={};self.available={}
        try:self.installed=set(subprocess.run(['pacman','-Qq'],capture_output=True,text=True).stdout.splitlines())
        except OSError:pass
        for i,g in enumerate(CAT):
            parent=QTreeWidgetItem(self.tree,[g['name']]);parent.setFlags(parent.flags()|Qt.ItemFlag.ItemIsAutoTristate|Qt.ItemFlag.ItemIsUserCheckable);parent.setCheckState(0,Qt.CheckState.Unchecked);parent.setFirstColumnSpanned(True);font=parent.font(0);font.setBold(True);parent.setFont(0,font)
            for key in g['packages']:
                name,desc=META[key];c=QTreeWidgetItem(parent,[name+'\n'+key,desc,'Kurulu' if key in self.installed else 'Kontrol edilecek']);c.setData(0,Qt.ItemDataRole.UserRole,('package',key));c.setCheckState(0,Qt.CheckState.Unchecked);c.setIcon(0,app_icon(key,name));c.setToolTip(0,name+' • '+key);c.setToolTip(1,desc)
            for key,name in EXTRAS.get(i,[]):
                c=QTreeWidgetItem(parent,[name,EXTRA_DESC[key],'İsteğe bağlı']);c.setData(0,Qt.ItemDataRole.UserRole,('extra',key));c.setCheckState(0,Qt.CheckState.Unchecked);c.setIcon(0,app_icon(key,name));c.setToolTip(1,EXTRA_DESC[key])
            if i in MANUAL:
                c=QTreeWidgetItem(parent,['Elle kurulum / genel rehber',MANUAL[i],'Rehber / manuel']);c.setToolTip(1,MANUAL[i]);c.setIcon(0,QIcon.fromTheme('help-contents'))
        self.tree.expandAll();self.tree.itemChanged.connect(lambda *_:self.count_selection())
        row=QHBoxLayout();right.addLayout(row)
        for label,fn in [('Tüm paketler',lambda:self.select_mode('packages')),('Yalnız eksikler',lambda:self.select_mode('missing')),('Görünenleri seç',lambda:self.select_mode('visible')),('Temizle',lambda:self.select_mode('none'))]:
            b=QPushButton(label);b.clicked.connect(fn);row.addWidget(b)
        row=QHBoxLayout();right.addLayout(row)
        self.single=QPushButton('Bu uygulamayı kur');self.single.clicked.connect(lambda:self.install_single(True));row.addWidget(self.single)
        self.singlepreview=QPushButton('Bu uygulamayı önizle');self.singlepreview.clicked.connect(lambda:self.install_single(False));row.addWidget(self.singlepreview)
        b=QPushButton('Görünen seçimleri kaldır');b.clicked.connect(lambda:self.select_mode('visible-clear'));row.addWidget(b)
        self.aur=QCheckBox('AUR: PKGBUILD incelemesi yapıldı');self.update=QCheckBox('Önce tam sistem güncellemesi');opts=QHBoxLayout();layout.addLayout(opts);opts.addWidget(self.aur);opts.addWidget(self.update);opts.addStretch()
        row=QHBoxLayout();layout.addLayout(row);self.refreshbutton=QPushButton('Durumları yenile');self.refreshbutton.clicked.connect(self.refresh_status);row.addWidget(self.refreshbutton)
        self.upgradebutton=QPushButton('Sistem / AUR / Flatpak güncelle');self.upgradebutton.clicked.connect(lambda:self.go(True,[('system-update','Tam güncelleme')]));row.addWidget(self.upgradebutton)
        self.preview=QPushButton('Kurulum planı');self.preview.clicked.connect(lambda:self.go(False));row.addWidget(self.preview);self.start=QPushButton('Seçilenleri kur');self.start.setObjectName('primary');self.start.clicked.connect(lambda:self.go(True));row.addWidget(self.start)
        self.bar=QProgressBar();layout.addWidget(self.bar);self.logs=QPlainTextEdit();self.logs.setReadOnly(True);self.logs.setMaximumHeight(115);self.logs.setPlaceholderText('İşlem günlüğü burada gösterilir. Kurulum başlamadan önce planı inceleyebilirsiniz.');layout.addWidget(self.logs)
        self.search.textChanged.connect(self.filter);self.categories.currentRowChanged.connect(lambda _:self.filter(self.search.text()));self.statusfilter.currentIndexChanged.connect(lambda _:self.filter(self.search.text()));self.refresh_status();self.count_selection()
    def refresh_status(self):
        try:
            r=subprocess.run(['pacman','-Q'],capture_output=True,text=True,check=True)
            self.versions=dict(line.split(maxsplit=1) for line in r.stdout.splitlines() if ' ' in line)
            self.installed=set(self.versions)
        except Exception as e:self.logs.appendPlainText('Paket kontrolü başarısız: '+str(e));return
        for c in self.children():
            d=c.data(0,Qt.ItemDataRole.UserRole)
            if not d:continue
            if d[0]=='package':
                k=d[1];old=self.versions.get(k,'');new=self.available.get(k,'');c.setText(2,'Güncelleme var' if old and new and old!=new else 'Kurulu' if old else 'Kurulu değil');c.setText(3,old);c.setText(4,new if old and old!=new else '')
            elif d[1] in ('docker-service','duplicati','opensnitch','libvirt'):
                unit={'docker-service':'docker','duplicati':'duplicati','opensnitch':'opensnitchd','libvirt':'libvirtd'}[d[1]]
                c.setText(2,'Aktif' if runcheck(['systemctl']+(['--user'] if unit=='duplicati' else [])+['is-active','--quiet',unit]) else 'Aktif değil')
            elif d[1] in ('portainer','mssql'):
                name='portainer' if d[1]=='portainer' else 'mssql2022'
                c.setText(2,'Mevcut' if runcheck(['sudo','-n','docker','container','inspect',name]) else 'Yok / erişilemedi')
        for c in self.children():
            status=c.text(2);color={'Kurulu':'#198754','Aktif':'#198754','Mevcut':'#198754','Güncelleme var':'#c27b21','Kurulu değil':'#b34a42','Aktif değil':'#b34a42'}.get(status)
            if color:c.setForeground(2,QBrush(QColor(color)))
            else:c.setData(2,Qt.ItemDataRole.ForegroundRole,None)
        self.filter(self.search.text())
    def scan_updates(self):
        if hasattr(self,'scan') and self.scan.isRunning():return
        self.scanbutton.setEnabled(False);self.logs.appendPlainText('Depo ve AUR güncellemeleri kontrol ediliyor…');self.scan=UpdateScan();self.scan.result.connect(self.scan_finished);self.scan.start()
    def scan_finished(self,updates,note):
        self.available=updates;self.refresh_status();self.logs.appendPlainText(note+' | '+str(len(updates))+' sistem paketi için güncelleme bulundu.');self.scanbutton.setEnabled(True)
    def children(self):
        for i in range(self.tree.topLevelItemCount()):
            p=self.tree.topLevelItem(i)
            for j in range(p.childCount()):yield p.child(j)
    def count_selection(self):
        rows=[c for c in self.children() if c.data(0,Qt.ItemDataRole.UserRole)]
        checked=[c for c in rows if c.checkState(0)==Qt.CheckState.Checked]
        packages=sum(c.data(0,Qt.ItemDataRole.UserRole)[0]=='package' for c in checked)
        self.summary.setText(f'Seçili: {len(checked)} / {len(rows)} işlem  •  {packages} paket  •  {len(checked)-packages} yapılandırma (gizli satırlar dahil)')
    def select_mode(self,mode):
        for c in self.children():
            d=c.data(0,Qt.ItemDataRole.UserRole)
            if not d:continue
            if mode.startswith('visible') and (c.isHidden() or c.parent().isHidden()):continue
            yes=mode in ('all','visible') or (d[0]=='package' and (mode=='packages' or (mode=='missing' and d[1] not in self.installed)))
            c.setCheckState(0,Qt.CheckState.Checked if yes else Qt.CheckState.Unchecked)
        self.count_selection()
    def install_single(self,apply=True):
        c=self.tree.currentItem()
        d=c.data(0,Qt.ItemDataRole.UserRole) if c else None
        if not d:
            QMessageBox.information(self,'Tekil seçim','Önce bir uygulama veya işlem satırına tıklayın.');return
        self.go(bool(apply),[tuple(d)])
    def filter(self,s):
        cat=self.categories.currentRow();status=self.statusfilter.currentIndex();s=s.casefold()
        for i in range(self.tree.topLevelItemCount()):
            p=self.tree.topLevelItem(i);match=s in p.text(0).casefold();visible=False
            for j in range(p.childCount()):
                c=p.child(j);d=c.data(0,Qt.ItemDataRole.UserRole);st=c.text(2)
                status_ok=(status==0 or (status==1 and st in ('Kurulu','Aktif','Mevcut','Güncelleme var')) or (status==2 and st in ('Kurulu değil','Aktif değil','Yok / erişilemedi')) or (status==3 and st=='Güncelleme var') or (status==4 and (not d or d[0]=='extra')))
                v=(cat==0 or cat==i+1) and status_ok and (match or s in (c.text(0)+' '+c.text(1)).casefold());c.setHidden(not v);visible|=v
            p.setHidden(not visible)
            if visible:p.setExpanded(True)
    def append(self,s):
        self.logs.appendPlainText(s)
        with self.logfile.open('a') as f:f.write(s+'\n')
    def go(self,apply,only=None):
        if hasattr(self,"worker") and self.worker.isRunning():return
        items=only if only is not None else [tuple(c.data(0,Qt.ItemDataRole.UserRole)) for c in self.children() if c.checkState(0)==Qt.CheckState.Checked and c.data(0,Qt.ItemDataRole.UserRole)]
        items.sort(key=lambda x: (0 if x[0]=='package' else 1 if x[1]=='docker-service' else 2))
        if not items:return
        missing=any(k=='package' and v not in self.installed for k,v in items)
        do_update=self.update.isChecked() or missing or any(k=='system-update' for k,v in items)
        if apply and all(k=='package' and v in self.installed for k,v in items) and not do_update:
            QMessageBox.information(self,'Kurulu','Seçilen paketler zaten kurulu. Güncelleme için ayrı düğmeyi kullanın.');return
        password=''
        if apply:
            if os.geteuid()==0 or not shutil.which('pacman'):QMessageBox.warning(self,'Uyarı','CachyOS üzerinde normal kullanıcı olarak çalıştırın.');return
            if QMessageBox.question(self,'Onay',f'{len(items)} işlem uygulanacak. '+ ('Tam sistem güncellemesi de yapılacak. ' if do_update else '')+'Docker erişimi ve grup yetkileri ayrıcalıklıdır. Devam?')!=QMessageBox.StandardButton.Yes:return
            if self.aur.isChecked() and QMessageBox.question(self,'AUR','AUR kodunu önceden incelediniz mi? Sessiz derleme üçüncü taraf kodu çalıştırır.')!=QMessageBox.StandardButton.Yes:return
            if ('extra','mssql') in items and not runcheck(['sudo','-n','docker','container','inspect','mssql2022']):
                password,ok=QInputDialog.getText(self,'SQL Server','Güçlü SA şifresi (Docker ortamında saklanır):',QLineEdit.EchoMode.Password)
                if not ok or not password:return
        self.logfile=STATE/('run-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.log');self.logs.clear();self.bar.setValue(0);self.start.setEnabled(False);self.preview.setEnabled(False);self.single.setEnabled(False);self.singlepreview.setEnabled(False);self.upgradebutton.setEnabled(False);self.worker=Worker(items,apply,self.aur.isChecked(),password,do_update);self.worker.log.connect(self.append);self.worker.progress.connect(self.bar.setValue);self.worker.done.connect(self.finish);self.worker.start()
    def finish(self,good,bad):
        self.append(f'Bitirildi: {good} başarılı/planlandı; {bad} başarısız/atlandı. Günlük: {self.logfile}');self.start.setEnabled(True);self.preview.setEnabled(True);self.single.setEnabled(True);self.singlepreview.setEnabled(True)
        self.available={};self.refresh_status();self.upgradebutton.setEnabled(True)
    def closeEvent(self,event):
        if (hasattr(self,'worker') and self.worker.isRunning()) or (hasattr(self,'scan') and self.scan.isRunning()):event.ignore();return
        event.accept()
if __name__=='__main__':
    if os.geteuid()==0: sys.exit('Normal kullanıcı olarak çalıştırın.')
    app=QApplication(sys.argv);w=Window();w.show();sys.exit(app.exec())
