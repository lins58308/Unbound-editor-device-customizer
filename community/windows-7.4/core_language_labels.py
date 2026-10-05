"""Curated primary navigation and controller vocabulary for all nine languages."""
import json, pathlib
ROOT=pathlib.Path(__file__).resolve().parent/'locales'
CODES=('ja','ko','es','fr','de','pt','it','ru','id')
ROWS='''
按鍵|ボタン|버튼|Botones|Boutons|Tasten|Botões|Pulsanti|Кнопки|Tombol
設定|設定|설정|Ajustes|Paramètres|Einstellungen|Configurações|Impostazioni|Настройки|Pengaturan
應用程式|アプリ|앱|Aplicaciones|Applications|Anwendungen|Aplicativos|Applicazioni|Приложения|Aplikasi
外觀|外観|모양|Apariencia|Apparence|Darstellung|Aparência|Aspetto|Оформление|Tampilan
使用說明|使い方|사용 안내|Guía de uso|Guide d’utilisation|Benutzerhandbuch|Guia de uso|Guida all’uso|Руководство|Panduan
通用操作|共通操作|공통 조작|Controles comunes|Commandes communes|Gemeinsame Steuerung|Controles comuns|Controlli comuni|Общие действия|Kontrol umum
背景執行|バックグラウンド|백그라운드 실행|Segundo plano|Arrière-plan|Hintergrundbetrieb|Segundo plano|Esecuzione in background|Работа в фоне|Berjalan di latar belakang
語言|言語|언어|Idioma|Langue|Sprache|Idioma|Lingua|Язык|Bahasa
介面語言|表示言語|인터페이스 언어|Idioma de la interfaz|Langue de l’interface|Sprache der Oberfläche|Idioma da interface|Lingua dell’interfaccia|Язык интерфейса|Bahasa antarmuka
選擇介面語言|表示言語を選択|인터페이스 언어 선택|Elegir idioma|Choisir la langue|Sprache auswählen|Escolher idioma|Scegli la lingua|Выбрать язык|Pilih bahasa
立即套用|今すぐ適用|바로 적용|Aplicar ahora|Appliquer|Jetzt anwenden|Aplicar agora|Applica ora|Применить|Terapkan sekarang
儲存|保存|저장|Guardar|Enregistrer|Speichern|Salvar|Salva|Сохранить|Simpan
取消|キャンセル|취소|Cancelar|Annuler|Abbrechen|Cancelar|Annulla|Отмена|Batal
捨棄|破棄|변경 취소|Descartar|Ignorer les modifications|Verwerfen|Descartar|Scarta|Не сохранять|Buang perubahan
確定|OK|확인|Aceptar|OK|OK|OK|OK|ОК|OK
關閉|閉じる|닫기|Cerrar|Fermer|Schließen|Fechar|Chiudi|Закрыть|Tutup
返回|戻る|뒤로|Atrás|Retour|Zurück|Voltar|Indietro|Назад|Kembali
目前配置|現在の割り当て|현재 배치|Asignación actual|Configuration actuelle|Aktuelle Belegung|Mapeamento atual|Mappatura attuale|Текущая раскладка|Pemetaan saat ini
未設定|未設定|미설정|Sin asignar|Non attribué|Nicht belegt|Não atribuído|Non assegnato|Не назначено|Belum ditetapkan
旋鈕|ダイヤル|다이얼|Dial|Molette|Drehregler|Dial|Manopola|Колесо|Kenop
逐格|ジョグ|조그|Jog|Jog|Jog|Jog|Jog|Jog|Jog
逐格（Jog）|Jog|Jog|Jog|Jog|Jog|Jog|Jog|Jog|Jog
連續（Shuttle）|Shuttle|Shuttle|Shuttle|Shuttle|Shuttle|Shuttle|Shuttle|Shuttle|Shuttle
捲動（Scroll）|スクロール|스크롤|Desplazamiento|Défilement|Scrollen|Rolagem|Scorrimento|Прокрутка|Gulir
逐格移動|コマ送り|프레임 이동|Avanzar por fotogramas|Image par image|Einzelbildschritte|Avançar quadros|Avanza fotogrammi|Покадровое перемещение|Gerak per bingkai
開啟主視窗|メイン画面を開く|기본 창 열기|Abrir ventana principal|Ouvrir la fenêtre|Hauptfenster öffnen|Abrir janela principal|Apri finestra principale|Открыть главное окно|Buka jendela utama
收至背景|トレイに収納|트레이로 숨기기|Ocultar en la bandeja|Réduire dans la zone de notification|In Infobereich ausblenden|Ocultar na bandeja|Nascondi nell’area di notifica|Свернуть в трей|Sembunyikan ke baki sistem
結束程式|終了|종료|Salir|Quitter|Beenden|Sair|Esci|Выход|Keluar
顯示浮動按鍵面板|フローティングキーボードを表示|플로팅 키보드 표시|Mostrar teclado flotante|Afficher le clavier flottant|Schwebende Tastatur anzeigen|Mostrar teclado flutuante|Mostra tastiera flottante|Показать плавающую клавиатуру|Tampilkan papan tombol mengambang
浮動面板滑鼠穿透|パネルのクリック透過|패널 클릭 통과|Clics a través del panel|Clics à travers le panneau|Klicks durch das Panel|Cliques através do painel|Clic attraverso il pannello|Пропуск кликов через панель|Klik menembus panel
面板穿透|クリック透過|클릭 통과|Clics a través|Clics à travers|Klickdurchlässig|Cliques através|Clic passanti|Пропуск кликов|Klik tembus
滑鼠左鍵選取|左クリック|왼쪽 클릭|Clic izquierdo|Clic gauche|Linksklick|Clique esquerdo|Clic sinistro|Левый клик|Klik kiri
滑鼠右鍵選單|右クリック|오른쪽 클릭|Clic derecho|Clic droit|Rechtsklick|Clique direito|Clic destro|Правый клик|Klik kanan
滑鼠雙擊|ダブルクリック|더블 클릭|Doble clic|Double clic|Doppelklick|Clique duplo|Doppio clic|Двойной клик|Klik ganda
旋鈕移動左右|マウスを左右に移動|마우스 좌우 이동|Mover ratón izquierda/derecha|Déplacer la souris à gauche/droite|Maus links/rechts bewegen|Mover mouse esquerda/direita|Sposta mouse a sinistra/destra|Мышь влево/вправо|Gerakkan mouse kiri/kanan
旋鈕移動上下|マウスを上下に移動|마우스 상하 이동|Mover ratón arriba/abajo|Déplacer la souris en haut/bas|Maus auf/ab bewegen|Mover mouse para cima/baixo|Sposta mouse su/giù|Мышь вверх/вниз|Gerakkan mouse atas/bawah
按住拖曳選取|長押しでドラッグ選択|누른 채 드래그 선택|Mantener para arrastrar|Maintenir pour faire glisser|Zum Ziehen gedrückt halten|Segurar para arrastar|Tieni premuto per trascinare|Удерживать для перетаскивания|Tahan untuk menyeret
複製|コピー|복사|Copiar|Copier|Kopieren|Copiar|Copia|Копировать|Salin
貼上|貼り付け|붙여넣기|Pegar|Coller|Einfügen|Colar|Incolla|Вставить|Tempel
剪下|切り取り|잘라내기|Cortar|Couper|Ausschneiden|Recortar|Taglia|Вырезать|Potong
復原|元に戻す|실행 취소|Deshacer|Annuler|Rückgängig|Desfazer|Annulla azione|Отменить действие|Urungkan
重做|やり直す|다시 실행|Rehacer|Rétablir|Wiederholen|Refazer|Ripeti|Повторить|Ulangi
搜尋|検索|검색|Buscar|Rechercher|Suchen|Pesquisar|Cerca|Поиск|Cari
隱藏|非表示|숨기기|Ocultar|Masquer|Ausblenden|Ocultar|Nascondi|Скрыть|Sembunyikan
全選|すべて選択|모두 선택|Seleccionar todo|Tout sélectionner|Alles auswählen|Selecionar tudo|Seleziona tutto|Выделить всё|Pilih semua
編輯|編集|편집|Editar|Modifier|Bearbeiten|Editar|Modifica|Изменить|Edit
新增|追加|추가|Añadir|Ajouter|Hinzufügen|Adicionar|Aggiungi|Добавить|Tambah
刪除|削除|삭제|Eliminar|Supprimer|Löschen|Excluir|Elimina|Удалить|Hapus
重新命名|名前を変更|이름 변경|Renombrar|Renommer|Umbenennen|Renomear|Rinomina|Переименовать|Ubah nama
重新整理|更新|새로 고침|Actualizar|Actualiser|Aktualisieren|Atualizar|Aggiorna|Обновить|Segarkan
恢復預設|初期設定に戻す|기본값 복원|Restaurar valores predeterminados|Rétablir les valeurs par défaut|Standard wiederherstellen|Restaurar padrões|Ripristina valori predefiniti|Восстановить по умолчанию|Pulihkan bawaan
重設|リセット|초기화|Restablecer|Réinitialiser|Zurücksetzen|Redefinir|Reimposta|Сбросить|Atur ulang
重試|再試行|다시 시도|Reintentar|Réessayer|Erneut versuchen|Tentar novamente|Riprova|Повторить попытку|Coba lagi
說明|ヘルプ|도움말|Ayuda|Aide|Hilfe|Ajuda|Aiuto|Справка|Bantuan
開啟|開く|열기|Abrir|Ouvrir|Öffnen|Abrir|Apri|Открыть|Buka
連線|接続|연결|Conectar|Connecter|Verbinden|Conectar|Connetti|Подключить|Hubungkan
登入|ログイン|로그인|Iniciar sesión|Se connecter|Anmelden|Entrar|Accedi|Войти|Masuk
登出|ログアウト|로그아웃|Cerrar sesión|Se déconnecter|Abmelden|Sair da conta|Esci dall’account|Выйти из аккаунта|Keluar akun
匯入…|インポート…|가져오기…|Importar…|Importer…|Importieren…|Importar…|Importa…|Импорт…|Impor…
匯出…|エクスポート…|내보내기…|Exportar…|Exporter…|Exportieren…|Exportar…|Esporta…|Экспорт…|Ekspor…
下一頁|次のページ|다음 페이지|Página siguiente|Page suivante|Nächste Seite|Próxima página|Pagina successiva|Следующая страница|Halaman berikutnya
上一頁|前のページ|이전 페이지|Página anterior|Page précédente|Vorherige Seite|Página anterior|Pagina precedente|Предыдущая страница|Halaman sebelumnya
下一個項目|次の項目|다음 항목|Elemento siguiente|Élément suivant|Nächster Eintrag|Próximo item|Elemento successivo|Следующий элемент|Item berikutnya
上一個項目|前の項目|이전 항목|Elemento anterior|Élément précédent|Vorheriger Eintrag|Item anterior|Elemento precedente|Предыдущий элемент|Item sebelumnya
頁面微捲|細かいページスクロール|미세 페이지 스크롤|Desplazamiento fino|Défilement fin|Feines Scrollen|Rolagem fina|Scorrimento fine|Плавная прокрутка|Gulir halus
頁面捲動|ページスクロール|페이지 스크롤|Desplazamiento de página|Défilement de page|Seite scrollen|Rolagem de página|Scorrimento pagina|Прокрутка страницы|Gulir halaman
音量|音量|음량|Volumen|Volume|Lautstärke|Volume|Volume|Громкость|Volume
提高系統音量|システム音量を上げる|시스템 음량 높이기|Subir volumen del sistema|Augmenter le volume système|Systemlautstärke erhöhen|Aumentar volume do sistema|Aumenta volume di sistema|Увеличить громкость системы|Naikkan volume sistem
降低系統音量|システム音量を下げる|시스템 음량 낮추기|Bajar volumen del sistema|Baisser le volume système|Systemlautstärke verringern|Diminuir volume do sistema|Riduci volume di sistema|Уменьшить громкость системы|Turunkan volume sistem
系統靜音|システム消音|시스템 음소거|Silenciar sistema|Couper le son système|System stummschalten|Silenciar sistema|Disattiva audio di sistema|Отключить звук системы|Bisukan sistem
播放／暫停媒體|メディア再生／一時停止|미디어 재생/일시 정지|Reproducir/pausar medios|Lire/mettre en pause|Medien abspielen/pausieren|Reproduzir/pausar mídia|Riproduci/pausa media|Воспроизведение/пауза|Putar/jeda media
播放／暫停|再生／一時停止|재생/일시 정지|Reproducir/pausar|Lire/pause|Wiedergabe/Pause|Reproduzir/pausar|Riproduci/pausa|Воспроизведение/пауза|Putar/jeda
播放|再生|재생|Reproducir|Lire|Abspielen|Reproduzir|Riproduci|Воспроизвести|Putar
暫停|一時停止|일시 정지|Pausar|Pause|Pausieren|Pausar|Pausa|Пауза|Jeda
停止|停止|정지|Detener|Arrêter|Stoppen|Parar|Ferma|Остановить|Hentikan
確認／開啟|確定／開く|확인/열기|Confirmar/abrir|Valider/ouvrir|Bestätigen/öffnen|Confirmar/abrir|Conferma/apri|Подтвердить/открыть|Konfirmasi/buka
中止|中止|중단|Interrumpir|Abandonner|Abbrechen|Interromper|Interrompi|Прервать|Hentikan
全部皆是|すべてはい|모두 예|Sí a todo|Oui à tout|Ja, alle|Sim para todos|Sì a tutto|Да для всех|Ya untuk semua
全部皆否|すべていいえ|모두 아니요|No a todo|Non à tout|Nein, alle|Não para todos|No a tutto|Нет для всех|Tidak untuk semua
是|はい|예|Sí|Oui|Ja|Sim|Sì|Да|Ya
否|いいえ|아니요|No|Non|Nein|Não|No|Нет|Tidak
名稱|名前|이름|Nombre|Nom|Name|Nome|Nome|Название|Nama
大小|サイズ|크기|Tamaño|Taille|Größe|Tamanho|Dimensione|Размер|Ukuran
類型|種類|유형|Tipo|Type|Typ|Tipo|Tipo|Тип|Jenis
位置|位置|위치|Ubicación|Position|Position|Posição|Posizione|Положение|Posisi
功能|機能|기능|Función|Fonction|Funktion|Função|Funzione|Функция|Fungsi
來源|ソース|소스|Fuente|Source|Quelle|Fonte|Sorgente|Источник|Sumber
偏好設定|環境設定|환경 설정|Preferencias|Préférences|Voreinstellungen|Preferências|Preferenze|Настройки|Preferensi
設定檔|プロファイル|프로필|Perfil|Profil|Profil|Perfil|Profilo|Профиль|Profil
入點|イン点|인 지점|Punto de entrada|Point d’entrée|In-Punkt|Ponto de entrada|Punto di attacco|Точка входа|Titik masuk
出點|アウト点|아웃 지점|Punto de salida|Point de sortie|Out-Punkt|Ponto de saída|Punto di stacco|Точка выхода|Titik keluar
靈敏度：|感度：|감도:|Sensibilidad:|Sensibilité :|Empfindlichkeit:|Sensibilidade:|Sensibilità:|Чувствительность:|Sensitivitas:
不透明度|不透明度|불투명도|Opacidad|Opacité|Deckkraft|Opacidade|Opacità|Непрозрачность|Opasitas
動作：|アクション：|동작:|Acción:|Action :|Aktion:|Ação:|Azione:|Действие:|Tindakan:
類別：|カテゴリ：|범주:|Categoría:|Catégorie :|Kategorie:|Categoria:|Categoria:|Категория:|Kategori:
還原未儲存變更|未保存の変更を元に戻す|저장하지 않은 변경 취소|Revertir cambios sin guardar|Annuler les modifications non enregistrées|Ungespeicherte Änderungen verwerfen|Reverter alterações não salvas|Annulla modifiche non salvate|Отменить несохранённые изменения|Batalkan perubahan belum disimpan
儲存失敗|保存に失敗しました|저장 실패|Error al guardar|Échec de l’enregistrement|Speichern fehlgeschlagen|Falha ao salvar|Salvataggio non riuscito|Ошибка сохранения|Gagal menyimpan
儲存設定檔|プロファイルを保存|프로필 저장|Guardar perfil|Enregistrer le profil|Profil speichern|Salvar perfil|Salva profilo|Сохранить профиль|Simpan profil
載入設定檔|プロファイルを読み込む|프로필 불러오기|Cargar perfil|Charger le profil|Profil laden|Carregar perfil|Carica profilo|Загрузить профиль|Muat profil
雲端設定檔|クラウドプロファイル|클라우드 프로필|Perfiles en la nube|Profils dans le cloud|Cloud-Profile|Perfis na nuvem|Profili cloud|Облачные профили|Profil cloud
重新自動掃描|自動スキャンを再実行|자동 검색 다시 실행|Volver a detectar aplicaciones|Relancer la détection automatique|Automatisch neu suchen|Detectar aplicativos novamente|Ripeti rilevamento automatico|Повторить поиск приложений|Pindai aplikasi lagi
顯示浮動面板|フローティングパネルを表示|플로팅 패널 표시|Mostrar panel flotante|Afficher le panneau flottant|Schwebendes Panel anzeigen|Mostrar painel flutuante|Mostra pannello flottante|Показать плавающую панель|Tampilkan panel mengambang
影片進度|再生位置|재생 위치|Posición del vídeo|Position de lecture|Videoposition|Posição do vídeo|Posizione video|Позиция видео|Posisi video
播放速度|再生速度|재생 속도|Velocidad de reproducción|Vitesse de lecture|Wiedergabegeschwindigkeit|Velocidade de reprodução|Velocità di riproduzione|Скорость воспроизведения|Kecepatan pemutaran
程式其他功能|アプリの追加操作|앱 추가 기능|Más controles de la aplicación|Autres commandes de l’application|Weitere App-Steuerungen|Mais controles do aplicativo|Altri controlli dell’app|Дополнительные действия|Kontrol aplikasi lainnya
12 種語言均可離線使用。|12 言語すべてオフラインで使用できます。|12개 언어 모두 오프라인에서 사용할 수 있습니다.|Los 12 idiomas funcionan sin conexión.|Les 12 langues fonctionnent hors ligne.|Alle 12 Sprachen funktionieren offline.|Os 12 idiomas funcionam offline.|Tutte le 12 lingue funzionano offline.|Все 12 языков работают без интернета.|Semua 12 bahasa dapat digunakan tanpa internet.
'''

def apply():
    dictionaries={code:json.loads((ROOT/(code+'.json')).read_text(encoding='utf8')) for code in CODES}
    for line in ROWS.strip().splitlines():
        source,*values=line.split('|');assert len(values)==len(CODES),source
        for code,value in zip(CODES,values):dictionaries[code][source]=value
    for code,dictionary in dictionaries.items():
        for prefix in ('逐格（Jog）','連續（Shuttle）','捲動（Scroll）'):
            assert prefix in dictionary
        (ROOT/(code+'.json')).write_text(json.dumps(dictionary,ensure_ascii=False,indent=2),encoding='utf8')
    print('Curated core labels applied to nine catalogs')

if __name__=='__main__':apply()
