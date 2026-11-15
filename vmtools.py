"""Standalone, unprivileged disk converter and explicit NetworkManager bridge workflow."""
import json, os, pathlib, re, shutil, subprocess, tempfile, uuid
from PySide6.QtCore import QProcess
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QLabel,QLineEdit,QPushButton,QFileDialog,QCheckBox,QMessageBox,QPlainTextEdit,QProgressBar,QComboBox,QApplication)

def output(args):
    return subprocess.check_output(args,text=True,stderr=subprocess.STDOUT,timeout=15).strip()

class DiskDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent);self.setWindowTitle('Sanal disk dönüştürme');self.resize(720,520)
        l=QVBoxLayout(self);l.addWidget(QLabel('VHDX / VHD / VDI / VMDK / QCOW2 → QCOW2. Kaynak disk değiştirilmez.'))
        self.src=QLineEdit();self.src.setReadOnly(True);l.addWidget(self.src)
        b=QPushButton('Kaynak disk seç');b.clicked.connect(self.pick);l.addWidget(b)
        self.dst=QLineEdit();self.dst.setReadOnly(True);l.addWidget(self.dst)
        b=QPushButton('Hedef QCOW2 seç');b.clicked.connect(self.target);l.addWidget(b)
        self.compress=QCheckBox('Sıkıştır (-c)');self.compress.setChecked(True);l.addWidget(self.compress)
        self.off=QCheckBox('Kaynak VM kapalı, checkpoint zinciri birleştirildi ve yedeğim var');l.addWidget(self.off)
        self.start=QPushButton('Alanı kontrol et ve dönüştür');self.start.clicked.connect(self.convert);l.addWidget(self.start)
        self.bar=QProgressBar();l.addWidget(self.bar);self.log=QPlainTextEdit();self.log.setReadOnly(True);l.addWidget(self.log)
        self.proc=QProcess(self);self.proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels);self.proc.readyReadStandardOutput.connect(self.read);self.proc.finished.connect(self.finish);self.proc.errorOccurred.connect(self.error);self.phase='';self.work=None;self.checkbuf='';self.final=None
    def pick(self):
        p,_=QFileDialog.getOpenFileName(self,'Kaynak disk','','Sanal diskler (*.vhdx *.vhd *.vdi *.vmdk *.qcow2);;Tüm dosyalar (*)')
        if p:self.src.setText(p);self.dst.setText(str(pathlib.Path(p).with_suffix('.converted.qcow2')))
    def target(self):
        p,_=QFileDialog.getSaveFileName(self,'Yeni hedef disk',self.dst.text(),'QCOW2 (*.qcow2)')
        if p:self.dst.setText(p)
    def convert(self):
        if not self.off.isChecked(): QMessageBox.warning(self,'Kontrol','Önce kaynak VM ve yedek koşullarını doğrulayın.');return
        try:
            if not shutil.which('qemu-img'):raise ValueError('Önce qemu-full paketini kurun.')
            a=pathlib.Path(self.src.text()).resolve(strict=True);b=pathlib.Path(self.dst.text()).absolute()
            if not self.dst.text() or not a.is_file() or b.suffix.lower()!='.qcow2' or b.exists() or b.is_symlink():raise ValueError('Yeni, mevcut olmayan .qcow2 hedefi seçin.')
            info=json.loads(output(['qemu-img','info','--output=json',str(a)]));fmt=info['format']
            if fmt not in ('vhdx','vpc','vdi','vmdk','qcow2'):raise ValueError('Desteklenmeyen kaynak biçimi: '+fmt)
            if info.get('backing-filename'):raise ValueError('Backing disk zinciri bulundu; önce birleştirin.')
            m=json.loads(output(['qemu-img','measure','--output=json','-f',fmt,'-O','qcow2',str(a)]));free=shutil.disk_usage(b.parent).free;need=m['required'];g=1024**3
            self.log.appendPlainText(f'Kaynak: {fmt} | Sanal kapasite: {info["virtual-size"]/g:.2f} GiB | Tahmin: {need/g:.2f} GiB | Boş: {free/g:.2f} GiB')
            if free < 2*g:raise ValueError('En az 2 GiB boş alan olmadan başlanmaz.')
            if free < need+2*g:
                if QMessageBox.question(self,'Alan uyarısı','Tahmini alan yetersiz. Sıkıştırma daha küçük çıktı verebilir fakat disk dolabilir. Başka hedef önerilir. Yine de denensin mi?')!=QMessageBox.StandardButton.Yes:return
            self.final=b;self.work=pathlib.Path(tempfile.mkdtemp(prefix='.csm-convert-',dir=b.parent))/'disk.qcow2';self.phase='convert';self.bar.setValue(0);self.start.setEnabled(False)
            self.proc.start('qemu-img',['convert','-p']+(['-c'] if self.compress.isChecked() else [])+['-f',fmt,'-O','qcow2',str(a),str(self.work)])
        except Exception as e: QMessageBox.warning(self,'Hata',str(e))
    def read(self):
        s=bytes(self.proc.readAllStandardOutput()).decode(errors='replace');self.checkbuf=(self.checkbuf+s)[-8192:];self.log.appendPlainText(s.strip())
        if self.phase=='convert':
            m=re.findall(r'([0-9.]+)/100%',self.checkbuf)
            if m:self.bar.setValue(int(float(m[-1])))
    def error(self,e):
        if e==QProcess.ProcessError.FailedToStart:self.fail('qemu-img başlatılamadı.')
    def fail(self,msg):
        self.log.appendPlainText(msg+' Geçici çıktı (varsa): '+str(self.work));self.start.setEnabled(True);self.phase=''
    def finish(self,code,status):
        self.read()
        if code or status!=QProcess.ExitStatus.NormalExit:self.fail('İşlem başarısız. Kaynak korunuyor.');return
        if self.phase=='convert':
            self.phase='check';self.checkbuf='';self.proc.start('qemu-img',['check','-f','qcow2',str(self.work)]);return
        if self.phase=='check':
            try:
                # Hard link is atomic and refuses to replace an existing destination.
                os.link(self.work,self.final);self.work.unlink();self.work.parent.rmdir();self.bar.setValue(100);self.log.appendPlainText('Dönüşüm ve QCOW2 yapısal kontrolü başarılı: '+str(self.final)+'\nVM açılışını ayrıca test edin.')
            except OSError as e:self.fail('Hedefe güvenli taşıma başarısız: '+str(e));return
            self.phase='';self.start.setEnabled(True)
    def reject(self):
        if self.proc.state()!=QProcess.ProcessState.NotRunning:QMessageBox.information(self,'İşlem sürüyor','Dönüşüm veya kontrol bitmeden pencereyi kapatmayın.');return
        super().reject()

class BridgeDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent);self.setWindowTitle('Ethernet ağ köprüsü (br0)');self.resize(720,480);l=QVBoxLayout(self)
        label=QLabel('Yalnız fiziksel kablolu Ethernet ve DHCP. Yerel konsoldan çalıştırın; bağlantı geçici kesilebilir. Wi-Fi, Docker ve NAT değiştirilmez.');label.setWordWrap(True);l.addWidget(label)
        self.devices=QComboBox();l.addWidget(self.devices);self.log=QPlainTextEdit();self.log.setReadOnly(True);l.addWidget(self.log)
        self.mapping={}
        try:
            for dev in output(['nmcli','-g','DEVICE','device','status']).splitlines():
                if not re.fullmatch(r'[a-zA-Z0-9_.-]+',dev) or not pathlib.Path('/sys/class/net',dev,'device').exists():continue
                if output(['nmcli','-g','GENERAL.TYPE','device','show',dev])!='ethernet':continue
                u=output(['nmcli','-g','GENERAL.CON-UUID','device','show',dev]);
                if not re.fullmatch(r'[0-9a-fA-F-]{36}',u):continue
                self.mapping[dev]=u;self.devices.addItem(dev)
        except Exception as e:self.log.appendPlainText(str(e))
        b=QPushButton('Planı önizle');b.clicked.connect(lambda:self.plan(False));l.addWidget(b)
        b=QPushButton('Köprüyü oluştur (terminalde onaylı)');b.clicked.connect(lambda:self.plan(True));l.addWidget(b)
        self.pending=None
    def plan(self,apply):
        try:
            dev=self.devices.currentText();old=self.mapping[dev]
            if output(['nmcli','-g','ipv4.method','connection','show',old])!='auto':raise ValueError('Statik IP profilleri otomatik değiştirilmez.')
            names=output(['nmcli','-g','NAME','connection','show']).splitlines()
            if 'br0' in names or 'br0-port' in names or pathlib.Path('/sys/class/net/br0').exists():raise ValueError('br0 veya br0-port mevcut. Mevcut köprüye dokunulmadı.')
            oldauto=output(['nmcli','-g','connection.autoconnect','connection','show',old]);a=str(uuid.uuid4());b=str(uuid.uuid4())
            import shlex
            cmds=[['sudo','nmcli','con','add','type','bridge','ifname','br0','con-name','br0','connection.uuid',a,'ipv4.method','auto','ipv6.method','auto','connection.autoconnect-ports','1'],['sudo','nmcli','con','add','type','ethernet','ifname',dev,'con-name','br0-port','connection.uuid',b,'master',a],['sudo','nmcli','con','mod',old,'connection.autoconnect','no'],['sudo','nmcli','con','down',old],['sudo','nmcli','con','up',b]]
            rollback=[['sudo','nmcli','con','delete',b],['sudo','nmcli','con','delete',a],['sudo','nmcli','con','mod',old,'connection.autoconnect',oldauto],['sudo','nmcli','con','up',old]]
            # Preserve exact plan so rollback uses only profiles created by this run.
            if not apply:self.pending=(dev,old,cmds,rollback)
            elif self.pending and self.pending[:2]==(dev,old):_,_,cmds,rollback=self.pending
            self.log.setPlainText('\n'.join(map(shlex.join,cmds))+'\n\nGeri alma:\n'+'\n'.join(map(shlex.join,rollback)))
            if not apply:return
            if QMessageBox.question(self,'Ağ değişikliği','Yerel konsoldasınız ve bağlantı kesintisini kabul ediyor musunuz?')!=QMessageBox.StandardButton.Yes:return
            rb='\n'.join(shlex.join(c)+' || true' for c in rollback)
            script='set -e\nsudo -v\nrollback(){\n'+rb+'\n}\ntrap rollback ERR\n'+ '\n'.join(map(shlex.join,cmds))+'\nfor i in {1..45}; do if ip -4 -o addr show dev br0 scope global | grep -q inet; then break; fi; sleep 1; done\nip -4 -o addr show dev br0 scope global | grep -q inet\ntrap - ERR\nip -4 -br addr\nbridge link\necho "Virt-Manager: köprü aygıtı br0. Geri alma komutları uygulamada gösteriliyor."\n'
            if not shutil.which('konsole'):raise ValueError('Konsole bulunamadı.')
            script += 'printf "%s\\n" '+shlex.quote('Geri alma komutları:\n'+'\n'.join(map(shlex.join,rollback)))+'\n'
            subprocess.Popen(['konsole','--hold','-e','bash','-c',script]);self.pending=None
        except Exception as e: QMessageBox.warning(self,'Köprü',str(e))
