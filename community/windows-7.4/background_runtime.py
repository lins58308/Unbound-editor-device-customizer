"""Keep the existing controller runtime alive behind a Windows system tray icon."""
import builtins
import copy
from PyQt6.QtCore import QEvent, QObject, QTimer, Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QHBoxLayout,
                            QLabel, QMenu, QPushButton, QSystemTrayIcon,
                            QVBoxLayout, QWidget)
import app
import config as cfg
import speed_editor_context as context
from speed_editor_context_icons import icon

DEFAULTS = {'close_to_tray': True, 'minimize_to_tray': True, 'start_hidden': False}


def preferences(config):
    saved = context.preferences(config).get('background', {})
    if not isinstance(saved, dict):
        saved = {}
    return {key: saved.get(key) if isinstance(saved.get(key), bool) else value
            for key, value in DEFAULTS.items()}


class BackgroundPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        title = QLabel('控制器持續運作，視窗留在背景')
        title.setStyleSheet('font-size:24px;font-weight:600;')
        title.setWordWrap(True)
        layout.addWidget(title)
        intro = QLabel('關閉或最小化主視窗後，可從右下角 Speed Editor 圖示重新開啟。'
                       '滑鼠控制、自動切換範本與浮動面板會繼續運作。')
        intro.setWordWrap(True)
        layout.addWidget(intro)
        group = QGroupBox('背景執行設定')
        form = QVBoxLayout(group)
        form.setSpacing(16)
        self.checks = {}
        for key, label in (('close_to_tray', '關閉主視窗時收至系統匣'),
                           ('minimize_to_tray', '最小化時收至系統匣'),
                           ('start_hidden', '下次啟動時直接在背景執行')):
            control = QCheckBox(label)
            control.setChecked(preferences(controller.owner._config)[key])
            control.toggled.connect(lambda value, name=key: controller.save(name, value))
            self.checks[key] = control
            form.addWidget(control)
        layout.addWidget(group)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        help_text = QLabel('雙擊系統匣圖示：開啟主視窗。右鍵：顯示浮動面板、解除面板穿透或結束程式。'
                           '若圖示被 Windows 隱藏，請展開右下角的「︿」。'
                           '要完全停止控制器，請在系統匣選「結束程式」。')
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        row = QHBoxLayout()
        self.hide_button = QPushButton('收至背景')
        self.hide_button.clicked.connect(controller.hide_window)
        row.addWidget(self.hide_button)
        guide = QPushButton('查看背景執行說明')
        guide.clicked.connect(controller.show_help)
        row.addWidget(guide)
        row.addStretch()
        layout.addLayout(row)
        layout.addStretch()

    def sync(self):
        settings = preferences(self.controller.owner._config)
        for key, control in self.checks.items():
            control.blockSignals(True)
            control.setChecked(settings[key])
            control.blockSignals(False)
        ready = self.controller.available()
        self.hide_button.setEnabled(ready)
        self.status.setText('系統匣圖示已啟用；設定立即儲存。' if ready else
                            '目前無法使用系統匣，主視窗會保留在畫面上，避免無法重新開啟。')


class Background(QObject):
    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.exiting = False
        self.stopped = False
        self.notified = False
        self.last_settings = None
        self.tray = QSystemTrayIcon(owner)
        image = owner.windowIcon()
        if image.isNull():
            image = QApplication.instance().windowIcon()
        if image.isNull():
            image = icon('controller')
        self.tray.setIcon(QIcon(image))
        self.menu = QMenu(owner)
        self.show_action = self.menu.addAction('開啟主視窗', self.show_window)
        self.show_action.setObjectName('trayShowMain')
        self.show_action.setFont(owner.font())
        self.hide_action = self.menu.addAction('收至背景', self.hide_window)
        self.menu.addSeparator()
        self.profile_action = self.menu.addAction('目前配置')
        self.profile_action.setEnabled(False)
        self.overlay_action = QAction('顯示浮動按鍵面板', self.menu)
        self.overlay_action.setCheckable(True)
        self.overlay_action.triggered.connect(owner._expanded_overlay.set_enabled)
        self.menu.addAction(self.overlay_action)
        self.passthrough_action = QAction('浮動面板滑鼠穿透', self.menu)
        self.passthrough_action.setCheckable(True)
        self.passthrough_action.triggered.connect(owner._expanded_overlay.set_locked)
        self.menu.addAction(self.passthrough_action)
        self.menu.addAction('使用說明', self.show_help)
        self.menu.addSeparator()
        self.quit_action = self.menu.addAction('結束程式', self.quit)
        self.quit_action.setObjectName('trayQuit')
        self.menu.setDefaultAction(self.show_action)
        self.menu.aboutToShow.connect(self.refresh)
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.activated)
        self.tray.messageClicked.connect(self.show_window)
        self.page = BackgroundPage(self)
        owner.centralWidget().addTab(self.page, '背景執行')
        owner._context.changed.connect(self.refresh)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        owner.installEventFilter(self)
        QApplication.instance().aboutToQuit.connect(self.cleanup)
        self.tray.show()
        self.refresh()
        QTimer.singleShot(0, self.initial_state)

    def available(self):
        return not self.stopped and QSystemTrayIcon.isSystemTrayAvailable() and self.tray.isVisible()

    def initial_state(self):
        if preferences(self.owner._config)['start_hidden']:
            self.hide_window()

    def refresh(self):
        if self.stopped:
            return
        layer_id = getattr(self.owner, '_runtime_layer_id', None) or self.owner._layer_id
        name = self.owner._config.get('layers', {}).get(layer_id, {}).get('name', '預設')
        name = str(name).replace('\n', ' ').replace('\r', ' ')[:70]
        self.profile_action.setText('目前配置：' + name)
        self.tray.setToolTip('Speed Editor 7.3\n目前配置：' + name + '\n雙擊開啟主視窗 · 右鍵開啟選單')
        panel = self.owner._expanded_overlay
        self.overlay_action.setChecked(panel.isVisible())
        self.passthrough_action.setChecked(panel.locked)
        self.hide_action.setEnabled(self.owner.isVisible() and self.available())
        settings = preferences(self.owner._config)
        if settings != self.last_settings:
            self.last_settings = settings
            self.page.sync()
        # Explorer may temporarily remove the notification area during restart.
        # Always provide a reachable window if the system tray is unavailable.
        if not QSystemTrayIcon.isSystemTrayAvailable() and not self.owner.isVisible():
            self.show_window()
        self.page.hide_button.setEnabled(self.available())

    def save(self, key, value):
        candidate = copy.deepcopy(self.owner._config)
        settings = preferences(candidate)
        settings[key] = bool(value)
        candidate['layers']['default'].setdefault('context_switching', {})['background'] = settings
        try:
            cfg.save(candidate)
        except (OSError, ValueError, TypeError) as error:
            self.page.sync()
            self.page.status.setText('設定尚未儲存：' + str(error))
            return False
        self.owner._config['layers']['default']['context_switching']['background'] = settings
        self.last_settings = None
        self.refresh()
        return True

    def hide_window(self, checked=False):
        if not self.available():
            self.owner.statusBar().showMessage('系統匣目前不可用，主視窗已保留。', 5000)
            return False
        self.owner.hide()
        if not self.notified:
            self.notified = True
            self.tray.showMessage('Speed Editor 持續在背景執行',
                                  '雙擊右下角圖示可開啟主視窗；右鍵可結束程式。',
                                  QSystemTrayIcon.MessageIcon.Information, 3500)
        self.refresh()
        return True

    def show_window(self, checked=False):
        if self.stopped:
            return
        self.owner.showNormal()
        self.owner.raise_()
        self.owner.activateWindow()
        self.refresh()

    def show_help(self, checked=False):
        self.show_window()
        self.owner._glass_help.search.setText('背景執行與系統匣')
        self.owner.centralWidget().setCurrentWidget(self.owner._glass_help)

    def activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger,
                      QSystemTrayIcon.ActivationReason.DoubleClick):
            self.show_window()

    def quit(self, checked=False):
        if self.exiting or self.stopped:
            return
        # Restore the editor first so its existing unsaved-changes dialog stays visible.
        self.show_window()
        self.exiting = True
        try:
            accepted = self.owner.close()
        finally:
            self.exiting = False
        if accepted:
            QApplication.instance().quit()

    def eventFilter(self, watched, event):
        if (watched is self.owner and event.type() == QEvent.Type.WindowStateChange
                and self.owner.isMinimized() and not self.exiting and not self.stopped
                and preferences(self.owner._config)['minimize_to_tray']):
            QTimer.singleShot(0, self.hide_if_minimized)
        return False

    def hide_if_minimized(self):
        if self.owner.isMinimized() and not self.exiting and not self.stopped:
            self.hide_window()

    def cleanup(self):
        if self.stopped:
            return
        self.stopped = True
        self.timer.stop()
        self.owner.removeEventFilter(self)
        self.menu.hide()
        self.tray.hide()


def install():
    if getattr(app, '_background_installed', False):
        return
    app._background_installed = True
    # The original config loader uses the Windows ANSI encoding. All extended
    # settings are saved as UTF-8, so read the same format through that loader
    # while retaining its existing migrations, defaults and recovery wrappers.
    def config_open(file, mode='r', *args, **kwargs):
        if mode == 'r' and not args and 'encoding' not in kwargs:
            kwargs['encoding'] = 'utf-8-sig'
        return builtins.open(file, mode, *args, **kwargs)
    cfg.open = config_open
    # Auto-discovered custom profile IDs are absent from the older icon table.
    import speed_editor_context_icons as icons
    original_vector = icons.vector_icon
    def vector(identifier, size=128):
        if identifier != 'controller' and identifier not in icons.PROFILES:
            identifier = 'general'
        return original_vector(identifier, size)
    icons.vector_icon = vector
    old_init = app.MainWindow.__init__
    old_close = app.MainWindow.closeEvent
    old_pressed = app.MainWindow._on_button_pressed

    def init(window, *args, **kwargs):
        old_init(window, *args, **kwargs)
        window.setWindowTitle(window.windowTitle().replace('7.2 · 統一滑鼠操作', '7.3 · 背景執行'))
        window._background = Background(window)
        QApplication.instance().setQuitOnLastWindowClosed(False)

    def close(window, event):
        controller = window._background
        application = QApplication.instance()
        if (not controller.exiting and not application.isSavingSession()
                and preferences(window._config)['close_to_tray'] and controller.available()):
            event.ignore()
            controller.hide_window()
            return
        old_close(window, event)
        if event.isAccepted():
            controller.cleanup()
            application.quit()

    def pressed(window, key):
        # The original hardware highlight also selects the editor button. When
        # the editor is hidden, that can display a modal unsaved-changes prompt
        # and block the input callback. The floating guide reads the live bridge
        # directly; keep the hidden editor selection and pending edits untouched.
        if not window.isVisible() and hasattr(window, '_background'):
            return
        return old_pressed(window, key)

    app.MainWindow.__init__ = init
    app.MainWindow.closeEvent = close
    app.MainWindow._on_button_pressed = pressed
