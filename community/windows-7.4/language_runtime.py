"""Offline display localization. Python getters retain source/config semantics.

Catalogs are injected by the builder, never downloaded by the running app.
No input values, paths, credentials, OBS names or hardware enums are translated.
"""
import copy
import html
import re
from PyQt6 import sip
from PyQt6.QtCore import QObject, QEvent, QLocale, QTimer, QTranslator, Qt, QRectF
from PyQt6.QtGui import QAction, QPainter
from PyQt6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMenu,
    QMessageBox, QPushButton, QStatusBar, QSystemTrayIcon, QTabBar, QTabWidget,
    QTableWidget, QTableWidgetItem,
    QTextBrowser, QTextEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)
import app
import config as cfg
import speed_editor_context as context

LANGUAGES = (('zh-TW', '繁體中文'), ('zh-CN', '简体中文'), ('en', 'English'),
    ('ja', '日本語'), ('ko', '한국어'), ('es', 'Español'), ('fr', 'Français'),
    ('de', 'Deutsch'), ('pt', 'Português'), ('it', 'Italiano'),
    ('ru', 'Русский'), ('id', 'Bahasa Indonesia'))
CODES = {code for code, name in LANGUAGES}
CATALOGS = {}
NATIVE = {}
SOURCE_ROLE = int(Qt.ItemDataRole.UserRole) + 18474
_ENGINE = None
SOURCE_PROPERTY = '_speedEditorLanguageSource'
SOURCE_ITEM_ROLE = SOURCE_ROLE + 1


class SourceValues:
    """Qt owns this metadata, independently of temporary Python wrappers."""
    def __init__(self):
        self.values = {}


def preference(config):
    value = context.preferences(config).get('ui_language', 'zh-TW')
    return value if isinstance(value, str) and value in CODES else 'zh-TW'


def tr(text):
    return _ENGINE.translate(text) if _ENGINE else text


def original(obj, key, fallback):
    return sources(obj).get(key, fallback())


def sources(obj):
    if isinstance(obj, QObject):
        value = obj.property(SOURCE_PROPERTY)
        if not isinstance(value, SourceValues):
            value = SourceValues()
            obj.setProperty(SOURCE_PROPERTY, value)
    elif isinstance(obj, QTreeWidgetItem):
        value = obj.data(0, SOURCE_ITEM_ROLE)
        if not isinstance(value, SourceValues):
            value = SourceValues()
            obj.setData(0, SOURCE_ITEM_ROLE, value)
    else:
        value = obj.data(SOURCE_ITEM_ROLE)
        if not isinstance(value, SourceValues):
            value = SourceValues()
            obj.setData(SOURCE_ITEM_ROLE, value)
    return value.values


def skip(obj):
    return bool(getattr(obj, '_language_skip', False) or
                (isinstance(obj, QComboBox) and obj.isEditable()))


def property_adapter(cls, setter, getter, rich=False):
    write, read = getattr(cls, setter), getattr(cls, getter)
    key = cls.__name__ + '.' + getter
    NATIVE[(cls, setter)] = write
    NATIVE[(cls, getter)] = read
    def set_value(obj, text):
        sources(obj)[key] = text
        visible = _ENGINE.html(text) if rich and _ENGINE else tr(text)
        return write(obj, text if skip(obj) else visible)
    def get_value(obj):
        return original(obj, key, lambda: read(obj))
    setattr(cls, setter, set_value)
    setattr(cls, getter, get_value)
    return cls, setter, getter, key, rich


PROPERTIES = []


class StandardTranslator(QTranslator):
    WORDS = {'Save': '儲存', 'Cancel': '取消', 'Discard': '捨棄', 'OK': '確定',
        'Yes': '是', 'No': '否', 'Close': '關閉', 'Apply': '套用', 'Retry': '重試',
        'Reset': '重設', 'Open': '開啟', 'Help': '說明', 'Abort': '中止',
        'Ignore': '略過', 'Restore Defaults': '恢復預設', 'Save All': '全部儲存',
        'Yes to All': '全部皆是', 'No to All': '全部皆否',
        'File name:': '檔案名稱：', 'Files of type:': '檔案類型：',
        'Look in:': '尋找位置：', 'Directory:': '資料夾：',
        'Back': '返回', 'Forward': '下一頁', 'Parent Directory': '上一層資料夾',
        'New Folder': '新增資料夾', 'List View': '清單檢視', 'Detail View': '詳細檢視',
        'Name': '名稱', 'Size': '大小', 'Type': '類型', 'Date Modified': '修改日期'}
    def translate(self, context_name, source, disambiguation=None, n=-1):
        plain = source.replace('&', '')
        chinese = self.WORDS.get(plain)
        if chinese:
            if _ENGINE.language == 'en':
                return plain
            return tr(chinese)
        return ''


class Engine(QObject):
    def __init__(self, application):
        super().__init__(application)
        self.language = 'zh-TW'
        self.cache = {}
        self.pending = False
        self.stopped = False
        self.translator = StandardTranslator(self)
        old = getattr(application, '_zh_tw_translator', None)
        if old:
            application.removeTranslator(old)
        application.installTranslator(self.translator)
        application.installEventFilter(self)
        application.aboutToQuit.connect(self.cleanup)

    def translate(self, text):
        if not isinstance(text, str) or not text:
            return text
        text = StandardTranslator.WORDS.get(text.replace('&', ''), text)
        if self.language == 'zh-TW': return text
        if text in self.cache:
            return self.cache[text]
        dictionary = CATALOGS.get(self.language, {})
        visible = dictionary.get(text)
        if visible is None:
            stripped = text.strip()
            if stripped in dictionary:
                visible = text.replace(stripped, dictionary[stripped], 1)
            else:
                visible = self.fragments.sub(lambda m: dictionary[m.group()], text) if self.fragments else text
                # A dynamic Chinese prefix should leave room for its value.
                if re.search(r'[\u3400-\u9fff]', text):
                    visible = visible.replace('：', ': ').replace('，', ', ').replace('；', '; ')
        if len(self.cache) > 8192:
            self.cache.clear()
        self.cache[text] = visible
        return visible

    def html(self, value):
        if not re.search(r'</?[a-z][^>]*>', value, re.I): return self.translate(value)
        parts = re.split(r'(<[^>]+>)', value)
        in_style = False
        for index, part in enumerate(parts):
            if index % 2:
                if re.match(r'<(?:style|script)\b', part, re.I): in_style = True
                if re.match(r'</(?:style|script)\b', part, re.I): in_style = False
            elif not in_style:
                decoded = html.unescape(part)
                parts[index] = html.escape(self.translate(decoded), quote=False)
        return ''.join(parts)

    def protect(self, owner):
        panel = owner.action_panel
        owner.layer_tabs._language_skip = True
        for name in ('window_list', 'audio_app_list', 'obs_scene', 'layer_push_combo'):
            widget = getattr(panel, name, None)
            if widget:
                widget._language_skip = True
        # Layer names and cloud profile names belong to the user.
        for widget in (getattr(owner, '_layer_combo', None),
                       getattr(owner, 'layer_combo', None)):
            if widget:
                widget._language_skip = True
        for widget in owner.findChildren(QComboBox):
            if widget.isEditable():
                widget._language_skip = True

    def refresh_object(self, obj):
        if sip.isdeleted(obj): return
        for cls, setter, getter, key, rich in PROPERTIES:
            if isinstance(obj, cls):
                values = sources(obj)
                if key not in values: values[key] = NATIVE[(cls, getter)](obj)
                source = values[key]
                display = source if skip(obj) else (self.html(source) if rich else self.translate(source))
                if NATIVE[(cls, getter)](obj) != display:
                    NATIVE[(cls, setter)](obj, display)
        if isinstance(obj, QComboBox):
            blocked = obj.blockSignals(True)
            for index in range(obj.count()):
                source = obj.itemData(index, SOURCE_ROLE)
                if source is None:
                    source = NATIVE[(QComboBox, 'itemText')](obj, index)
                    obj.setItemData(index, source, SOURCE_ROLE)
                NATIVE[(QComboBox, 'setItemText')](obj, index, source if skip(obj) else self.translate(source))
            obj.blockSignals(blocked)
        if isinstance(obj, QTabBar):
            blocked = obj.blockSignals(True)
            for index in range(obj.count()):
                key = ('tab', index)
                source = sources(obj).setdefault(key, NATIVE[(QTabBar, 'tabText')](obj, index))
                NATIVE[(QTabBar, 'setTabText')](obj, index, source if skip(obj) else self.translate(source))
            obj.blockSignals(blocked)
        if isinstance(obj, QListWidget):
            for index in range(obj.count()): refresh_item(obj.item(index))
        if isinstance(obj, QTableWidget):
            for column in range(obj.columnCount()):
                refresh_item(obj.horizontalHeaderItem(column))
            for row in range(obj.rowCount()):
                refresh_item(obj.verticalHeaderItem(row))
                for column in range(obj.columnCount()): refresh_item(obj.item(row,column))
        if isinstance(obj, QTreeWidget):
            def walk(item):
                for column in range(obj.columnCount()): refresh_tree_item(item, column)
                for index in range(item.childCount()): walk(item.child(index))
            for index in range(obj.topLevelItemCount()): walk(obj.topLevelItem(index))
            walk(obj.headerItem())
        if isinstance(obj, QTextBrowser) and getattr(obj, '_language_html', None) is not None:
            display = self.html(obj._language_html)
            if getattr(obj, '_language_rendered_html', None) != display:
                obj._language_rendered_html = display
                scroll = obj.verticalScrollBar().value()
                NATIVE[(QTextEdit, 'setHtml')](obj, display)
                obj.verticalScrollBar().setValue(scroll)

    def refresh(self):
        self.pending = False
        if self.stopped: return
        application = QApplication.instance()
        roots = application.topLevelWidgets()
        for root in roots:
            for obj in [root] + root.findChildren(QObject):
                self.refresh_object(obj)
            root.update()

    def set_language(self, code):
        if code not in CODES: code = 'zh-TW'
        self.language = code
        self.cache.clear()
        dictionary = CATALOGS.get(code, {})
        keys = [key for key in dictionary if len(key) >= 2 and re.search(r'[\u3400-\u9fff]', key)]
        self.fragments = re.compile('|'.join(re.escape(key) for key in sorted(keys, key=len, reverse=True))) if keys else None
        QLocale.setDefault(QLocale(code.replace('-', '_')))
        self.refresh()
        for root in QApplication.topLevelWidgets():
            if hasattr(root, '_glass_help'):
                root._glass_help.filter(root._glass_help.search.text())
                panel = root._expanded_overlay
                panel.last_signature = None
                panel.refresh()
                root._background.refresh()
            root.update()

    def eventFilter(self, watched, event):
        if not self.stopped and event.type() == QEvent.Type.Show:
            if not self.pending:
                self.pending = True
                QTimer.singleShot(0, self.refresh)
        return False

    def cleanup(self):
        self.stopped = True
        application = QApplication.instance()
        application.removeEventFilter(self)
        application.removeTranslator(self.translator)


def refresh_item(item):
    if item is None or sip.isdeleted(item): return
    key = 'listText'
    cls = QTableWidgetItem if isinstance(item,QTableWidgetItem) else QListWidgetItem
    source = sources(item).setdefault(key, NATIVE[(cls, 'text')](item))
    NATIVE[(cls, 'setText')](item, source if skip(item) else tr(source))


def refresh_tree_item(item, column):
    if item is None or sip.isdeleted(item): return
    key = ('treeText', column)
    source = sources(item).setdefault(key, NATIVE[(QTreeWidgetItem, 'text')](item, column))
    NATIVE[(QTreeWidgetItem, 'setText')](item, column, source if skip(item) else tr(source))


def install_adapters():
    for cls, setter, getter in ((QWidget, 'setWindowTitle', 'windowTitle'),
        (QWidget, 'setToolTip', 'toolTip'), (QWidget, 'setStatusTip', 'statusTip'),
        (QLabel, 'setText', 'text'), (QAbstractButton, 'setText', 'text'),
        (QGroupBox, 'setTitle', 'title'), (QAction, 'setText', 'text'),
        (QAction, 'setToolTip', 'toolTip'), (QMenu, 'setTitle', 'title'),
        (QLineEdit, 'setPlaceholderText', 'placeholderText'),
        (QSystemTrayIcon, 'setToolTip', 'toolTip')):
        PROPERTIES.append(property_adapter(cls, setter, getter, cls == QLabel))

    # Model role is separate from existing UserRole IDs and custom item data.
    for name in ('addItem', 'insertItem', 'addItems', 'insertItems', 'setItemText',
                 'itemText', 'currentText', 'findText', 'setCurrentText', 'clear'):
        NATIVE[(QComboBox, name)] = getattr(QComboBox, name)
    def add(obj, *args, **kwargs):
        result = NATIVE[(QComboBox, 'addItem')](obj, *args, **kwargs)
        index = obj.count() - 1
        source = NATIVE[(QComboBox, 'itemText')](obj, index)
        obj.setItemData(index, source, SOURCE_ROLE)
        if not skip(obj): NATIVE[(QComboBox, 'setItemText')](obj, index, tr(source))
        return result
    def insert(obj, index, *args, **kwargs):
        before = obj.count()
        result = NATIVE[(QComboBox, 'insertItem')](obj, index, *args, **kwargs)
        if obj.count() > before:
            index = max(0, min(index, before))
            source = NATIVE[(QComboBox, 'itemText')](obj, index)
            obj.setItemData(index, source, SOURCE_ROLE)
            if not skip(obj): NATIVE[(QComboBox, 'setItemText')](obj, index, tr(source))
        return result
    def item_text(obj, index):
        source = obj.itemData(index, SOURCE_ROLE)
        return source if source is not None else NATIVE[(QComboBox, 'itemText')](obj, index)
    def current(obj):
        return NATIVE[(QComboBox, 'currentText')](obj) if obj.isEditable() else item_text(obj, obj.currentIndex())
    def set_item(obj, index, text):
        obj.setItemData(index, text, SOURCE_ROLE)
        return NATIVE[(QComboBox, 'setItemText')](obj, index, text if skip(obj) else tr(text))
    def find(obj, text, *args):
        for index in range(obj.count()):
            if item_text(obj, index) == text: return index
        return NATIVE[(QComboBox, 'findText')](obj, text, *args)
    def set_current(obj, text):
        index = find(obj, text)
        if index >= 0: return obj.setCurrentIndex(index)
        return NATIVE[(QComboBox, 'setCurrentText')](obj, text)
    QComboBox.addItem = add
    QComboBox.insertItem = insert
    QComboBox.addItems = lambda obj, texts: [add(obj, text) for text in texts] and None
    QComboBox.insertItems = lambda obj, index, texts: [insert(obj, index + i, text) for i, text in enumerate(texts)] and None
    QComboBox.setItemText = set_item
    QComboBox.itemText = item_text
    QComboBox.currentText = current
    QComboBox.findText = find
    QComboBox.setCurrentText = set_current

    for name in ('tabText', 'setTabText', 'addTab', 'insertTab', 'removeTab'):
        NATIVE[(QTabBar, name)] = getattr(QTabBar, name)
    def tab_text(obj, index):
        return original(obj, ('tab', index), lambda: NATIVE[(QTabBar, 'tabText')](obj, index))
    def set_tab(obj, index, text):
        sources(obj)[('tab', index)] = text
        return NATIVE[(QTabBar, 'setTabText')](obj, index, text if skip(obj) else tr(text))
    QTabBar.tabText = tab_text
    QTabBar.setTabText = set_tab
    # QTabWidget has its own C++ facade; keep its source getter stable as well.
    NATIVE[(QTabWidget, 'tabText')] = QTabWidget.tabText
    NATIVE[(QTabWidget, 'setTabText')] = QTabWidget.setTabText
    QTabWidget.tabText = lambda obj, index: tab_text(obj.tabBar(), index)
    QTabWidget.setTabText = lambda obj, index, text: set_tab(obj.tabBar(), index, text)
    def tab_mutation(cls, name):
        native = getattr(cls, name)
        NATIVE[(cls, name)] = native
        def mutate(obj, *args):
            bar = obj.tabBar() if isinstance(obj, QTabWidget) else obj
            labels = [tab_text(bar, index) for index in range(bar.count())]
            result = native(obj, *args)
            if name == 'removeTab':
                if 0 <= args[0] < len(labels): labels.pop(args[0])
            else:
                label = next(value for value in reversed(args) if isinstance(value, str))
                labels.insert(result, label)
            values = sources(bar)
            for key in list(values):
                if isinstance(key, tuple) and key[0] == 'tab': values.pop(key)
            for index, label in enumerate(labels):
                values[('tab', index)] = label
                NATIVE[(QTabBar, 'setTabText')](bar, index, label if skip(bar) else tr(label))
            return result
        setattr(cls, name, mutate)
    for cls in (QTabWidget, QTabBar):
        for name in ('addTab', 'insertTab', 'removeTab'): tab_mutation(cls, name)

    for cls in (QListWidgetItem, QTableWidgetItem, QTreeWidgetItem):
        for name in ('text', 'setText'): NATIVE[(cls, name)] = getattr(cls, name)
    QListWidgetItem.text = lambda obj: original(obj, 'listText', lambda: NATIVE[(QListWidgetItem, 'text')](obj))
    def set_list(obj, text):
        sources(obj)['listText'] = text
        return NATIVE[(QListWidgetItem, 'setText')](obj, text if skip(obj) else tr(text))
    QListWidgetItem.setText = set_list
    QTableWidgetItem.text = lambda obj: original(obj, 'listText', lambda: NATIVE[(QTableWidgetItem, 'text')](obj))
    def set_table(obj, text):
        sources(obj)['listText'] = text
        return NATIVE[(QTableWidgetItem, 'setText')](obj, text if skip(obj) else tr(text))
    QTableWidgetItem.setText = set_table
    QTreeWidgetItem.text = lambda obj, column: original(obj, ('treeText', column), lambda: NATIVE[(QTreeWidgetItem, 'text')](obj, column))
    def set_tree(obj, column, text):
        sources(obj)[('treeText', column)] = text
        return NATIVE[(QTreeWidgetItem, 'setText')](obj, column, text if skip(obj) else tr(text))
    QTreeWidgetItem.setText = set_tree
    for cls, name in ((QStatusBar, 'showMessage'), (QSystemTrayIcon, 'showMessage')):
        old = getattr(cls, name)
        def message(obj, *args, _old=old, **kwargs):
            return _old(obj, *(tr(arg) if isinstance(arg, str) else arg for arg in args), **kwargs)
        setattr(cls, name, message)
    NATIVE[(QTextEdit, 'setHtml')] = QTextEdit.setHtml
    def set_html(obj, text):
        obj._language_html = text
        display = _ENGINE.html(text) if _ENGINE else text
        obj._language_rendered_html = display
        return NATIVE[(QTextEdit, 'setHtml')](obj, display)
    QTextEdit.setHtml = set_html
    for name in ('information', 'question', 'warning', 'critical', 'about'):
        old = getattr(QMessageBox, name)
        def dialog(parent, title, text, *args, _old=old, **kwargs):
            return _old(parent, tr(title), tr(text), *args, **kwargs)
        setattr(QMessageBox, name, staticmethod(dialog))
    # The main dial is painted rather than a text widget.
    paint = QPainter.drawText
    QPainter.drawText = lambda painter, *args: paint(painter, *(tr(arg) if isinstance(arg, str) else arg for arg in args))


class LanguagePage(QWidget):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.setObjectName('languagePage')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)
        title = QLabel('選擇介面語言')
        title.setStyleSheet('font-size:24px;font-weight:600;')
        title.setWordWrap(True)
        layout.addWidget(title)
        intro = QLabel('所有介面與浮動面板會立即更新。')
        intro.setWordWrap(True)
        layout.addWidget(intro)
        row = QHBoxLayout()
        row.addWidget(QLabel('介面語言'))
        self.combo = QComboBox()
        self.combo.setObjectName('uiLanguage')
        self.combo._language_skip = True
        for code, name in LANGUAGES: self.combo.addItem(name, code)
        self.combo.setCurrentIndex(self.combo.findData(preference(owner._config)))
        row.addWidget(self.combo, 1)
        self.apply = QPushButton('立即套用')
        self.apply.setObjectName('applyLanguage')
        self.apply.clicked.connect(self.save)
        row.addWidget(self.apply)
        layout.addLayout(row)
        note = QLabel('切換語言只改變顯示文字，按鍵配置與快捷鍵保持原值。\n12 種語言均可離線使用。')
        note.setWordWrap(True)
        layout.addWidget(note)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch()

    def save(self):
        code = self.combo.currentData()
        candidate = copy.deepcopy(self.owner._config)
        candidate['layers']['default'].setdefault('context_switching', {})['ui_language'] = code
        try:
            cfg.save(candidate)
        except (OSError, ValueError, TypeError) as error:
            self.combo.setCurrentIndex(self.combo.findData(preference(self.owner._config)))
            self.status.setText('設定尚未儲存：' + str(error))
            return False
        self.owner._config['layers']['default'].setdefault('context_switching', {})['ui_language'] = code
        _ENGINE.set_language(code)
        self.status.setText('語言已儲存，重新啟動後也會保留。')
        return True


def install():
    global _ENGINE
    if getattr(app, '_language_installed', False): return
    app._language_installed = True
    install_adapters()
    old_application = QApplication.__init__
    def application_init(application, *args, **kwargs):
        global _ENGINE
        old_application(application, *args, **kwargs)
        _ENGINE = Engine(application)
    QApplication.__init__ = application_init
    import speed_editor_glass_overlay as overlay
    old_layout = overlay.text_layout
    overlay.text_layout = lambda label, *args, **kwargs: old_layout(tr(label), *args, **kwargs)
    old_geometry = overlay.geometry
    def physical_geometry(board, controls):
        if board.panel.compact.isChecked(): return old_geometry(board, controls)
        # Use the original hardware constants. Translated button size hints in
        # the editor must never change the floating keyboard's physical map.
        rectangles = {}
        spacing, column, height = app.SPACING, app.SUBCOL_W, app.BTN_H
        left_width = 6*column+5*spacing
        middle_width = 8*column+7*spacing
        for definitions, dx in ((app._LEFT,0),(app._MIDDLE,left_width+20)):
            for row, col, span, key, label in definitions:
                y = row*(height+spacing) - (height-app.SPACER_H if row>2 else 0)
                rectangles[key] = QRectF(dx+col*(column+spacing),y,span*column+(span-1)*spacing,height)
        right_x = left_width+20+middle_width+20
        for key, label, x, y, width in app._RIGHT_ABS:
            rectangles[key] = QRectF(right_x+x,y,width,height)
        dial = QRectF(right_x,app.HALF_OFFSET+height+48,300,300)
        bounding = QRectF(dial)
        for rect in rectangles.values(): bounding = bounding.united(rect)
        scale = min((board.width()-14)/bounding.width(),(board.height()-14)/bounding.height())
        dx = (board.width()-bounding.width()*scale)/2
        dy = (board.height()-bounding.height()*scale)/2
        def mapped(rect):
            return QRectF(dx+(rect.x()-bounding.x())*scale,dy+(rect.y()-bounding.y())*scale,rect.width()*scale,rect.height()*scale)
        return [(key,label,action,mapped(rectangles[key])) for key,label,action in controls],mapped(dial),'hardware'
    overlay.geometry = physical_geometry
    import speed_editor_glass_help as guide
    def filter_guide(widget, text):
        current = widget.topics.currentItem()
        selected = current.data(Qt.ItemDataRole.UserRole) if current else 0
        widget.topics.blockSignals(True)
        widget.topics.clear()
        needle = text.casefold()
        for index, (title, keywords, body) in enumerate(guide.SECTIONS):
            translated = tr(title) + ' ' + tr(keywords) + ' ' + (_ENGINE.html(body) if _ENGINE else body)
            if needle not in (title + ' ' + keywords + ' ' + body + ' ' + translated).casefold(): continue
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, index)
            widget.topics.addItem(item)
            refresh_item(item)
            if index == selected: widget.topics.setCurrentItem(item)
        if widget.topics.currentRow() < 0 and widget.topics.count(): widget.topics.setCurrentRow(0)
        widget.topics.blockSignals(False)
        widget.render()
    guide.Guide.filter = filter_guide
    import speed_editor_usability as usability
    original_search = usability._search_entries
    class SearchableText(str):
        def casefold(self): return str.casefold(self) + ' ' + tr(str(self)).casefold()
    usability._search_entries = lambda owner: [(SearchableText(label),key) for label,key in original_search(owner)]
    import speed_editor_catalog as catalog
    def populate_commands(widget, *args):
        identifier = widget.applications.currentData()
        if identifier not in catalog.BY_ID: return
        application = catalog.BY_ID[identifier]
        assigned = catalog.assignments(identifier,[key for key in widget.owner.se_widget._btn_widgets if key!=widget.entry.currentData()])
        widget.info.setText(application['note'] or 'Windows 預設鍵位，可依你自己的設定修改。')
        widget.table.blockSignals(True)
        widget.table.setRowCount(0)
        needle = widget.search.text().strip().casefold()
        for index, command in enumerate(application['commands']):
            shortcut = widget.overrides.get((identifier,index),command['action'].get('keys','OBS 連線'))
            cells = [command['name'],shortcut,assigned[index],command['note']]
            searchable = ' '.join(cells) + ' ' + ' '.join(tr(cell) for cell in cells)
            if needle and needle not in searchable.casefold(): continue
            row = widget.table.rowCount()
            widget.table.insertRow(row)
            for column, value in enumerate(cells):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole,index)
                widget.table.setItem(row,column,item)
                refresh_item(item)
        widget.table.blockSignals(False)
        widget.table.resizeRowsToContents()
        widget.create_button.setText('建立配置層（'+str(len(application['commands']))+' 項）')
        if widget.table.rowCount(): widget.table.selectRow(0)
        widget._selection_changed()
    catalog.ApplicationLibrary._populate_commands = populate_commands
    # Existing hardware-description signals emit visible text from C++, so
    # aliases are added without changing Jog/Shuttle/Scroll serialization.
    for source, description in list(app._DIAL_HW_MODE_DESCS.items()):
        for dictionary in CATALOGS.values():
            if source in dictionary: app._DIAL_HW_MODE_DESCS[dictionary[source]] = description
    previous = app.MainWindow.__init__
    import speed_editor_background as background
    old_background_refresh = background.Background.refresh
    def background_refresh(controller):
        old_background_refresh(controller)
        if not controller.stopped:
            controller.tray.setToolTip(controller.tray.toolTip().replace('Speed Editor 7.3', 'Speed Editor 7.4'))
    background.Background.refresh = background_refresh
    def init(owner, *args, **kwargs):
        previous(owner, *args, **kwargs)
        owner.setWindowTitle(owner.windowTitle().replace('7.3 · 背景執行', '7.4 · 多語言'))
        owner._language_page = LanguagePage(owner)
        owner.centralWidget().addTab(owner._language_page, '語言')
        _ENGINE.protect(owner)
        _ENGINE.set_language(preference(owner._config))
    app.MainWindow.__init__ = init
