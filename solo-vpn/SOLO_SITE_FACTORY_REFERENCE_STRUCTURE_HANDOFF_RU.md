# Solo Site Factory — перенос шапки и геометрии из макетов (26.10.2026)

Полные исходники находятся в архиве **SOLO_SITE_FACTORY_REFERENCE_STRUCTURE_ENGINE.zip** в текущем разговоре, а не в этой GitHub-ветке. SHA256: 1a252d7e27046ba29291fec7a14b2cfd3b92b29c33c2718fd83dc746641eb8a0 (актуальная контрольная сумма в SOLO_FACTORY_REFERENCE_STRUCTURE_SHA256.json). База — скачанный настоящий архив SOLO_SITE_FACTORY_COMPOSITION_ENGINE.zip; ничего не начинать с нуля.

Добавлено engine/reference_structure.py: отдельное определение фона, контрастного текста и видимой высоты шапки из desktop/mobile макетов. Параметры сохраняются в editable BLUEPRINT.json → reference_structure; confidence low, approved false. Встроено в анализ и CSS build с разными media queries. При отсутствии явной границы прежний CSS не меняется; данные проверяются против CSS-инъекций. Добавлены 8 новых тестов и RUN_REFERENCE_STRUCTURE_WINDOWS.bat, REFERENCE_STRUCTURE_GUIDE_RU.md.

На трёх синтетических дизайнах 21 из 21 размеров и 6 из 6 Chromium offline browser comparisons технически успешны. Улучшение каталога ПК: raster 87.01→95.11%, contour 13.48→23.38%. Полная таблица также показывает небольшую деградацию contour у двух мобильных макетов; ни одну proxy метрику нельзя выдавать за художественную готовность. Созданы контактные листы до/после и separate site+engine ZIP.

Свежий Python QA нового кода: 130/130 быстрых тестов PASS; 27 тяжёлых браузерных тестов не подтверждены из-за ограничения времени среды; прежний полный результат 149/149 относится к предыдущему неизменённому движку, не к текущему. Clean unzip: 21/21 релевантных PASS, doctor.core_ready true на Linux/Python 3.13. Windows 10 физически не проверялся.

Solo VPN не изменён: публичный ZIP SOLO_VPN_SITE_SEPARATE_REFERENCE_STRUCTURE.zip, 91 файл, SHA256 3531da41ae8f11ddb4748018cd4dcdac6714134ba0fe9f777000b815a514b95f. Его старые настоящие браузерные кадры (ПК и телефон) отдельно в SOLO_VPN_REFERENCE_STRUCTURE_SCREENSHOTS.zip, а новый benchmark evidence в SOLO_FACTORY_REFERENCE_STRUCTURE_SCREENSHOTS_QA.zip.

Пять исторических оценок без роста: локальный сайт 100% в пределах старого QA; визуал ПК 90% и телефон 90% ручные; движок 90% старый локальный чек-лист; коммерческий VPN 49,5%, статус PRODUCTION_BLOCKED. Тесты не означают коммерческий релиз или обещание «200% лучше».

Далее: испытания Windows 10, настоящие неоднородные клиентские макеты, реальная публикация HTTPS, легальные загрузки и завершение 27 тяжёлых проверок. Только затем отдельная доводка сайта Solo VPN.
