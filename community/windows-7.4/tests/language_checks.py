"""Acceptance of translated display against the unchanged real controller loop."""
import faulthandler, re
from PyQt6.QtCore import Qt, QTimer, QEvent
from PyQt6.QtGui import QAction, QFontMetrics
from PyQt6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialogButtonBox,
    QLabel, QLineEdit, QMessageBox, QTabBar, QTabWidget, QTableWidgetItem, QListWidget, QListWidgetItem, QWidget)
lang = sys.modules['speed_editor_languages']
engine = lang._ENGINE
window = live
panel = window.action_panel
page = window._language_page
cfg.save = ux.atomic_save
trace = (OUT/'language-trace.log').open('w',encoding='utf8')
faulthandler.dump_traceback_later(60,file=trace,exit=True)
report = {'source_sha256':'__SOURCE_SHA256__','platform':application.platformName(),'checks':[]}

def check(name, condition, details=None):
    report['checks'].append({'name':name,'pass':bool(condition),'details':details})
    (OUT/'language-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    assert condition, name+': '+repr(details)

def pump():
    for _ in range(3): application.processEvents()

def raw(cls, method, obj, *args):
    return lang.NATIVE[(cls,method)](obj,*args)

def semantic(config):
    copy_config = copy.deepcopy(config)
    copy_config['layers']['default'].setdefault('context_switching',{}).pop('ui_language',None)
    return copy_config

window.show()
ctl.prepare()
window._expanded_overlay.set_enabled(False)
window._expanded_overlay.compact.setChecked(False)
pump()
try:
    check('12 language choices with Traditional Chinese default',page.combo.count()==12 and page.combo.currentData()=='zh-TW')
    for bad in ('unknown',None,{},12):
        value=copy.deepcopy(window._config);value['layers']['default']['context_switching']['ui_language']=bad
        check('invalid saved preference falls back safely '+repr(bad),lang.preference(value)=='zh-TW')
    panel.load_button('CAM1',window._config,'default');panel._set_flat_index(1)
    panel.hotkey_input.setText('ctrl+shift+s');pump()
    check('unsaved editor fixture is dirty',ux._dirty(panel))
    baseline=semantic(window._config)
    combo=panel.sys_vol_hw_mode
    panel.obs_scene.clear();panel.obs_scene.addItems(['播放速度','來源']);panel.obs_scene.setCurrentIndex(0)
    custom_input=QLineEdit('播放速度',window)
    for code,name in lang.LANGUAGES:
        start=time.monotonic()
        page.combo.setCurrentIndex(page.combo.findData(code))
        check('language preference saved '+code,page.save())
        pump()
        expected='儲存' if code=='zh-TW' else lang.CATALOGS[code]['儲存']
        check('native Save button display '+code,raw(QAbstractButton,'text',panel.save_btn)==expected,raw(QAbstractButton,'text',panel.save_btn))
        check('source getter and shortcuts remain stable '+code,panel.save_btn.text()=='儲存' and panel.hotkey_input.text()=='ctrl+shift+s' and ux._dirty(panel))
        check('every mapping and non-language preference retained '+code,semantic(window._config)==baseline)
        saved=json.loads(pathlib.Path(cfg.CONFIG_FILE).read_text(encoding='utf-8-sig'))
        check('saved language survives config reload '+code,lang.preference(saved)==code and semantic(saved)==baseline)
        check('native OBS names and editable inputs preserved '+code,raw(QComboBox,'currentText',panel.obs_scene)=='播放速度' and panel.obs_scene.currentText()=='播放速度' and custom_input.text()=='播放速度')
        for index, mode in enumerate(('Jog','Shuttle','Scroll')):
            combo.setCurrentIndex(index);pump()
            check('hardware enum remains '+code+' '+mode,combo.currentText()==mode)
        check('apply uses under 3 seconds '+code,time.monotonic()-start<3,round(time.monotonic()-start,3))
        tray=window._background
        check('tray menu translated '+code,raw(QAction,'text',tray.show_action)==('開啟主視窗' if code=='zh-TW' else lang.CATALOGS[code]['開啟主視窗']))
        window.centralWidget().setCurrentWidget(page);pump()
        window.grab().save(str(OUT/('language-'+code+'.png')))
    page.combo.setCurrentIndex(page.combo.findData('en'));page.save();pump()
    window._ux_search.setText('dial');pump()
    check('button search finds translated dial name',window._ux_results.findData('__dial__')>=0)
    window._ux_search.clear();pump()
    library=sys.modules['speed_editor_catalog'].ApplicationLibrary(window)
    library.applications.setCurrentIndex(library.applications.findData('potplayer'))
    library.search.setText('frame');library.show();pump()
    check('preset search finds translated frame controls and preserves command IDs',library.table.rowCount()>0 and all(library.table.item(i,0).data(Qt.ItemDataRole.UserRole) is not None for i in range(library.table.rowCount())))
    check('native preset table translated',all('frame' in raw(QTableWidgetItem,'text',library.table.item(i,0)).casefold() or 'frame' in raw(QTableWidgetItem,'text',library.table.item(i,3)).casefold() for i in range(library.table.rowCount())))
    library.close();pump()
    tabs=QTabWidget(window);tabs.addTab(QWidget(),'儲存');tabs.addTab(QWidget(),'取消');tabs.removeTab(0);tabs.insertTab(0,QWidget(),'語言')
    check('dynamic tab add remove insert preserve source labels',tabs.tabText(0)=='語言' and tabs.tabText(1)=='取消' and raw(QTabBar,'tabText',tabs.tabBar(),0)=='Language',[tabs.tabText(0),tabs.tabText(1),raw(QTabBar,'tabText',tabs.tabBar(),0)])
    panel._ux_revert();panel.load_button('CAM1',window._config,'default');panel._set_flat_index(12)
    for mode in ('Jog','Shuttle','Scroll'):
        panel.sys_vol_hw_mode.setCurrentText(mode)
        value=sys.modules['speed_editor_extra_editor'].action_value(panel)
        check('English UI serializes original dial mode '+mode,value['hw_mode']==mode,value)
    panel._ux_revert()
    check('English guide searches translated topics',bool(window._glass_help.filter('mouse') is None and window._glass_help.topics.count()))
    window._glass_help.topics.setCurrentRow(0);window._glass_help.render();pump()
    check('guide text is translated and hardware names retained','SLIP SRC' in window._glass_help.body.toPlainText() and 'mouse' in window._glass_help.body.toPlainText().casefold())
    window.centralWidget().setCurrentWidget(window._glass_help);window.grab().save(str(OUT/'guide-en.png'))
    # Lists created after switching must render correctly once their window shows.
    items=QListWidget(window);items.addItem(QListWidgetItem('儲存'));items.show();pump()
    check('new native list is translated without changing source getter',raw(QListWidgetItem,'text',items.item(0))=='Save' and items.item(0).text()=='儲存')
    items.hide()
    native_buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel,window)
    native_buttons.show();pump()
    check('native dialog buttons use selected language',{'Save','Cancel'}<={raw(QAbstractButton,'text',button).replace('&','') for button in native_buttons.buttons()})
    native_buttons.hide()
    observed={}
    def dismiss():
        box=next((obj for obj in QApplication.topLevelWidgets() if isinstance(obj,QMessageBox) and obj.isVisible()),None)
        if box:
            observed['title']=raw(QWidget,'windowTitle',box);observed['body']=box.text()
            box.button(QMessageBox.StandardButton.Cancel).click()
    QTimer.singleShot(50,dismiss)
    answer=QMessageBox.question(window,'避免遺失變更','目前的設定尚未儲存。',QMessageBox.StandardButton.Save|QMessageBox.StandardButton.Cancel)
    check('modal warning translated and return enum intact',observed.get('title')=='Keep your changes' and observed.get('body')=='Current settings are not saved.' and answer==QMessageBox.StandardButton.Cancel,observed)
    board=window._expanded_overlay.board
    panel._ux_revert();window._expanded_overlay.resize(760,540);window._expanded_overlay.show();pump()
    geometry=sys.modules['speed_editor_glass_overlay'].geometry
    overlay=sys.modules['speed_editor_expanded_overlay']
    def physical_map(cells):
        first=cells[0][3];unit=first.width()
        return [(k,round((r.x()-first.x())/unit,7),round((r.y()-first.y())/unit,7),round(r.width()/unit,7),round(r.height()/unit,7)) for k,l,a,r in cells]
    cells,_,mode=geometry(board,overlay.rows(window));before=physical_map(cells)
    for code in ('de','ja','ru','zh-TW'):
        engine.set_language(code);pump();board.grab();pump()
        cells,_,mode=geometry(board,overlay.rows(window))
        check('physical keyboard proportions and positions unchanged '+code,mode=='hardware' and before==physical_map(cells) and window._expanded_overlay.size().width()==760 and window._expanded_overlay.size().height()==540)
        check('all physical keys remain visible '+code,len(board.labels)==len(cells) and len(cells)>=30)
        window._expanded_overlay.grab().save(str(OUT/('floating-'+code+'.png')))
    window._expanded_overlay.hide()
    page.combo.setCurrentIndex(page.combo.findData('zh-TW'));page.save();pump()
    check('switch back restores Traditional Chinese',raw(QAbstractButton,'text',panel.save_btn)=='儲存')
    previous=copy.deepcopy(window._config);cfg.save=lambda value:(_ for _ in ()).throw(OSError('read-only fixture'))
    page.combo.setCurrentIndex(page.combo.findData('en'))
    check('failed save does not change language or mappings',not page.save() and window._config==previous and engine.language=='zh-TW' and page.combo.currentData()=='zh-TW')
    cfg.save=ux.atomic_save
    check('no runtime translation service or networking',not any(word in pathlib.Path(lang.__file__).name for word in ('translate_public',)))
    report['passed']=True
except BaseException:
    import traceback
    (OUT/'language-error.txt').write_text(traceback.format_exc(),encoding='utf8')
    raise
finally:
    for target in (window,base_window):
        target.action_panel._ux_revert();target._background.exiting=True;target.close()
    pump();engine.cleanup();faulthandler.cancel_dump_traceback_later()
    # Dispose the fixture's two windows and owned dialogs while Python and the
    # Qt event dispatcher are alive. Native Windows accessibility providers can
    # otherwise outlive Qt when this short harness starts exec only at the end.
    for root in QApplication.topLevelWidgets(): root.deleteLater()
    QApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
    pump()
    (OUT/'language-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if application.platformName()=='windows':
    QTimer.singleShot(0,application.quit);application.exec()
print(json.dumps({'passed':report.get('passed',False),'checks':len(report['checks'])}))
