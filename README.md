# Arvectum Proxy Launcher — Windows client

Локальный Windows-прокси с графическим лаунчером. Приложение поднимает HTTP proxy, SOCKS5 и PAC на `127.0.0.1`, направляет обычный трафик через внешний HTTP proxy клиента и пропускает домены из `no_proxy.txt` напрямую.

## Рекомендуемый сценарий поставки

Клиенту передаётся готовый `Arvectum Proxy Launcher.exe` вместе с `install.bat`, `uninstall.bat`, `uninstall.ps1`, `restore_network.bat` и `INSTALL.txt`. `install.bat` предпочитает EXE-версию, копирует её в `%USERPROFILE%\Documents\ArvectumProxyLauncher` и создаёт ярлык. Для готового EXE Python на клиентском компьютере не нужен.

Автозапуск установщик намеренно не включает. Сначала нужно заполнить внешний proxy, включить его и проверить соединение; после этого автозапуск можно включить галочкой в GUI.

## Порты по умолчанию

- HTTP proxy: `127.0.0.1:8080`
- SOCKS5: `127.0.0.1:1080`
- PAC: `http://127.0.0.1:8082/proxy.pac`

## Исправления release-candidate

- `no_proxy` применяется не только в PAC, но и внутри HTTP/SOCKS движка. Исключения работают для клиентов, которые используют `HTTP_PROXY/HTTPS_PROXY` или локальный SOCKS и игнорируют PAC.
- Доменное сопоставление гранично-безопасно: `zakupki.gov.ru` и его поддомены совпадают, `evilzakupki.gov.ru` — нет.
- Изменение списка исключений синхронизирует активный `NO_PROXY`; удалённое исключение не остаётся «залипшим» до перезапуска. Исходный пользовательский `NO_PROXY` при этом сохраняется.
- Перед изменением WinINET требуется корректная резервная копия. Если backup создать нельзя, системный proxy не включается.
- На время работы PAC устанавливается `ProxyEnable=0`, поэтому старый ручной `ProxyServer` пользователя не включается параллельно с PAC. Исходное значение потом восстанавливается.
- Пользовательские `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY` резервируются и восстанавливаются.
- Остановка больше не делает безусловный `taskkill /F` по старому PID. PID хранится вместе с Windows process creation time; при несовпадении или невозможности подтвердить идентичность процесс не завершается.
- `is_running()` проверяет собственный PAC endpoint, а не просто занятый TCP-порт.
- Запуск без настроенного upstream завершается до изменения сети.
- Пока proxy включён, создаётся временный recovery-autostart в `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`. Он защищает от reboot/crash, когда PAC мог бы остаться на localhost без работающего core. При нормальном выключении запись удаляется.
- CLI `--stop`/`--rollback` теперь возвращает ошибку, если WinINET/env восстановлены не полностью.
- `uninstall.bat` не удаляет приложение и backup-файлы, пока rollback не подтверждён как успешный. Это защищает от потери recovery-данных при сбое восстановления сети.
- RC2.1 добавляет owner marker каталога установки и проверку reparse-point/имени каталога перед рекурсивным удалением; installer/uninstaller удаляют scheduled task только при подтверждённой принадлежности этому EXE.
- GUI показывает незавершённый rollback как отдельное состояние, выделяет восстановление сети, объясняет следующий шаг при «Проверить» и предлагает recovery сразу при открытии приложения.
- Исправлены имена EXE, пути helper BAT и проверки `errorlevel` в CMD-скриптах.
- Cold-start ожидание увеличено, чтобы one-file PyInstaller/антивирус не давали ложную ошибку на первом запуске.
- `build_exe.bat` выполняет compile gate и unit tests до PyInstaller.

## Исключения

`no_proxy.txt` содержит по одному домену/маске на строку. Всегда напрямую идут как минимум `localhost`, `127.0.0.1`, `::1`, `*.local`, `10.*`, `192.168.*`. Домены можно добавлять/удалять через GUI; PAC, внутренний HTTP/SOCKS router и активный `NO_PROXY` обновляются без перезапуска.

## Проверка исходников

```bat
py -3 -m py_compile proxy_core.py proxy_gui.py
py -3 -m unittest -v tests.test_proxy_core
```

Текущий набор RC2.1: 37 unit/smoke/static release tests.

Сборка:

```bat
build_exe.bat
```

`build_exe.bat` сам выполняет compile/test gates и прерывает сборку при ошибке.

## Ограничения текущей частной сборки

- Upstream host/port остаются обычными настройками. Логин и пароль на Windows сохраняются единым `credentials_dpapi` blob (Windows DPAPI, current-user scope); plaintext `username`/`password` из RC2 автоматически мигрирует при первом чтении RC2.1. Если DPAPI не может защитить credentials, приложение не записывает их открытым текстом.
- Code signing в исходном комплекте не выполняется. Неподписанный EXE может получить SmartScreen/Unknown publisher. Это не исправляется Python-патчем: для релиза без предупреждений нужен сертификат подписи кода и подписанный installer/EXE.
- Failover между несколькими upstream сейчас в первую очередь транспортный: если TCP-соединение с первым upstream установилось, но сам proxy вернул 407/5xx, автоматический переход на следующий upstream не гарантирован. Для текущей поставки с одним рабочим upstream это не блокер; для публичного multi-proxy режима нужен отдельный hardening.
- WinHTTP-level proxy (`netsh winhttp`) не меняется. Приложения, которые игнорируют WinINET/PAC и proxy environment, могут требовать отдельной интеграции.

Финальный EXE обязательно собирать и принимать на реальной Windows-машине: Linux/macOS не могут подтвердить поведение WinINET, `schtasks`, PyInstaller Windows bootloader и точный rollback реестра.
