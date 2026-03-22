#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VideoVisualEffects v1.1 — Video Effects Processor
Applies pixel, wave, stripe, glitch and other effects to video files.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import time

try:
    import cv2
    import numpy as np
    BACKEND_AVAILABLE = True
except ImportError as e:
    BACKEND_AVAILABLE = False
    _BACKEND_ERROR = str(e)


# ─────────────────────────────────────────────────────────────────────────────
# TRANSLATIONS
# ─────────────────────────────────────────────────────────────────────────────

TRANSLATIONS = {
    'en': {
        'process': 'Process', 'settings': 'Settings',
        'input_file': 'Input File:', 'output_file': 'Output File (MP4):',
        'browse': 'Browse...', 'effect': 'Effect:',
        'start': 'Start Processing', 'stop': 'Stop', 'status': 'Status:',
        'ready': 'Ready', 'processing': 'Processing...', 'done': 'Done!',
        'stopped': 'Stopped', 'error': 'Error',
        'params_lf': 'Effect Parameters', 'info_lf': 'Information',
        'stat_elapsed': 'Elapsed:', 'stat_remaining': 'Remaining:',
        'stat_frame': 'Frame:', 'stat_fps': 'Source FPS:',
        'stat_res': 'Resolution:', 'stat_size': 'File size:',
        'out_fps': 'Output FPS:', 'out_fps_auto': '0 (auto)',
        'scale': 'Scale:', 'codec': 'Codec:',
        'hints_lf': 'Tips', 'language': 'Language:',
        'hints': (
            "• mp4v  — wide compatibility, larger file\n"
            "• avc1  — H.264, better compression (requires ffmpeg)\n"
            "• Scale 50% — halves the resolution\n"
            "• FPS=0 — keeps original video FPS\n"
            "• Audio track is not copied to the output"
        ),
        'select_input': 'Select input video',
        'select_output': 'Save result',
        'video_files': 'Video files', 'all_files': 'All files',
        'warn_no_input': 'Please select an input file!',
        'warn_no_output': 'Please specify an output file!',
        'done_title': 'Completed!',
        'done_msg': 'Processing finished in {t}.\n\nEffect:  {eff}\nFile:    {out}\nSize:    {sz}\nFrames:  {fr}',
        'err_title': 'Error',
        'err_msg': 'Processing failed after {t}.\n\n{e}',
        # Effect labels
        'fx_pixelate': 'Pixelate',
        'fx_wave':     'Wave',
        'fx_stripes':  'Stripes',
        'fx_glitch':   'Glitch',
        'fx_chromatic':'Chromatic Aberration',
        'fx_scanlines':'Scanlines',
        'fx_quantize': 'Color Quantize',
        'fx_vhs':      'VHS',
        'fx_rgb_shift':'RGB Shift',
        'fx_mirror':   'Mirror',
        'fx_neon':     'Neon',
        # Effect descriptions
        'desc_pixelate': 'Divides the frame into large square blocks, giving a retro pixel-art look.',
        'desc_wave':     'Bends rows or columns with a sine wave, creating a ripple distortion that animates over time.',
        'desc_stripes':  'Overlays dark horizontal or vertical bands, similar to window blinds or a film strip.',
        'desc_glitch':   'Randomly shifts horizontal slices and color channels each frame, simulating a corrupted digital signal.',
        'desc_chromatic':'Separates the red and blue color channels laterally, producing rainbow fringes on edges.',
        'desc_scanlines':'Darkens every N-th line, mimicking the CRT television scan-line effect.',
        'desc_quantize': 'Reduces the number of distinct color levels, creating a posterized, low-bit-depth look.',
        'desc_vhs':      'Combines scanlines, chromatic shift, noise and tape-flicker to emulate a worn VHS cassette.',
        'desc_rgb_shift':'Independently shifts the R, G and B channels in any direction, creating colorful ghosting.',
        'desc_mirror':   'Copies one half of the frame and flips it, producing a perfectly symmetrical image.',
        'desc_neon':     'Extracts edges and renders them as bright glowing lines on a dark background.',
        # Param labels
        'p_block_size':   'Block size (px)',
        'p_amplitude':    'Amplitude (px)',
        'p_frequency':    'Frequency',
        'p_axis':         'Direction',
        'p_stripe_width': 'Stripe width (px)',
        'p_opacity':      'Opacity (%)',
        'p_orientation':  'Orientation',
        'p_intensity':    'Intensity',
        'p_block_height': 'Block height (px)',
        'p_shift':        'Channel shift (px)',
        'p_line_gap':     'Line gap (px)',
        'p_darkness':     'Darkness (%)',
        'p_colors':       'Color levels',
        'p_noise':        'Noise',
        'p_track_error':  'Track error (px)',
        'p_r_shift':      'R shift (px)',
        'p_g_shift':      'G shift (px)',
        'p_b_shift':      'B shift (px)',
        'p_mode':         'Axis',
        'p_blur':         'Glow blur',
        'p_boost':        'Boost',
    },
    'ru': {
        'process': 'Обработка', 'settings': 'Настройки',
        'input_file': 'Входной файл:', 'output_file': 'Выходной файл (MP4):',
        'browse': 'Обзор...', 'effect': 'Эффект:',
        'start': 'Начать обработку', 'stop': 'Стоп', 'status': 'Статус:',
        'ready': 'Готово', 'processing': 'Обработка...', 'done': 'Готово!',
        'stopped': 'Остановлено', 'error': 'Ошибка',
        'params_lf': 'Параметры эффекта', 'info_lf': 'Информация',
        'stat_elapsed': 'Прошло:', 'stat_remaining': 'Осталось:',
        'stat_frame': 'Кадр:', 'stat_fps': 'FPS источника:',
        'stat_res': 'Разрешение:', 'stat_size': 'Размер файла:',
        'out_fps': 'Выходной FPS:', 'out_fps_auto': '0 (авто)',
        'scale': 'Масштаб:', 'codec': 'Кодек:',
        'hints_lf': 'Подсказки', 'language': 'Язык:',
        'hints': (
            "• mp4v  — широкая совместимость, больший размер\n"
            "• avc1  — H.264, лучшее сжатие (требует ffmpeg)\n"
            "• Масштаб 50% — уменьшает разрешение вдвое\n"
            "• FPS=0 — сохраняет оригинальный FPS видео\n"
            "• Аудиодорожка не переносится в выходной файл"
        ),
        'select_input': 'Выберите входное видео',
        'select_output': 'Сохранить результат',
        'video_files': 'Видео файлы', 'all_files': 'Все файлы',
        'warn_no_input': 'Выберите входной файл!',
        'warn_no_output': 'Укажите выходной файл!',
        'done_title': 'Завершено!',
        'done_msg': 'Обработка завершена за {t}.\n\nЭффект:  {eff}\nФайл:    {out}\nРазмер:  {sz}\nКадров:  {fr}',
        'err_title': 'Ошибка',
        'err_msg': 'Обработка завершилась с ошибкой за {t}.\n\n{e}',
        'fx_pixelate': 'Пиксели',
        'fx_wave':     'Волны',
        'fx_stripes':  'Полосы',
        'fx_glitch':   'Глитч',
        'fx_chromatic':'Хроматическая аберрация',
        'fx_scanlines':'Строки (scanlines)',
        'fx_quantize': 'Квантизация цвета',
        'fx_vhs':      'VHS',
        'fx_rgb_shift':'RGB Сдвиг',
        'fx_mirror':   'Зеркало',
        'fx_neon':     'Неон',
        'desc_pixelate': 'Делит кадр на крупные квадратные блоки, создавая эффект ретро-пикселизации.',
        'desc_wave':     'Изгибает строки или столбцы синусоидой — рябь, которая анимируется во времени.',
        'desc_stripes':  'Накладывает тёмные горизонтальные или вертикальные полосы, как жалюзи или плёнка.',
        'desc_glitch':   'Случайно сдвигает горизонтальные полосы и каналы цвета — имитация сбоя сигнала.',
        'desc_chromatic':'Разводит красный и синий каналы в стороны — радужные края, как у плохой оптики.',
        'desc_scanlines':'Затемняет каждую N-ю строку — эффект кинескопа старого телевизора.',
        'desc_quantize': 'Уменьшает количество цветовых уровней — постеризация, вид 8-битной графики.',
        'desc_vhs':      'Комбинирует строки, хроматику, шум и мерцание — эффект изношенной видеокассеты.',
        'desc_rgb_shift':'Независимо сдвигает каналы R, G, B — цветные «призраки» вокруг объектов.',
        'desc_mirror':   'Копирует половину кадра и отражает — идеально симметричное изображение.',
        'desc_neon':     'Выделяет края и рисует их как яркие светящиеся линии на тёмном фоне.',
        'p_block_size':   'Размер блока (px)',
        'p_amplitude':    'Амплитуда (px)',
        'p_frequency':    'Частота',
        'p_axis':         'Направление',
        'p_stripe_width': 'Ширина полосы (px)',
        'p_opacity':      'Прозрачность (%)',
        'p_orientation':  'Ориентация',
        'p_intensity':    'Интенсивность',
        'p_block_height': 'Высота блока (px)',
        'p_shift':        'Смещение каналов (px)',
        'p_line_gap':     'Шаг строки (px)',
        'p_darkness':     'Затемнение (%)',
        'p_colors':       'Кол-во оттенков',
        'p_noise':        'Шум',
        'p_track_error':  'Смещение трека (px)',
        'p_r_shift':      'Сдвиг R (px)',
        'p_g_shift':      'Сдвиг G (px)',
        'p_b_shift':      'Сдвиг B (px)',
        'p_mode':         'Ось',
        'p_blur':         'Размытие свечения',
        'p_boost':        'Усиление',
    },
    'uk': {
        'process': 'Обробка', 'settings': 'Налаштування',
        'input_file': 'Вхідний файл:', 'output_file': 'Вихідний файл (MP4):',
        'browse': 'Огляд...', 'effect': 'Ефект:',
        'start': 'Почати обробку', 'stop': 'Стоп', 'status': 'Статус:',
        'ready': 'Готово', 'processing': 'Обробка...', 'done': 'Готово!',
        'stopped': 'Зупинено', 'error': 'Помилка',
        'params_lf': 'Параметри ефекту', 'info_lf': 'Інформація',
        'stat_elapsed': 'Минуло:', 'stat_remaining': 'Залишилось:',
        'stat_frame': 'Кадр:', 'stat_fps': 'FPS джерела:',
        'stat_res': 'Роздільність:', 'stat_size': 'Розмір файлу:',
        'out_fps': 'Вихідний FPS:', 'out_fps_auto': '0 (авто)',
        'scale': 'Масштаб:', 'codec': 'Кодек:',
        'hints_lf': 'Підказки', 'language': 'Мова:',
        'hints': (
            "• mp4v  — широка сумісність, більший розмір\n"
            "• avc1  — H.264, краще стиснення (потребує ffmpeg)\n"
            "• Масштаб 50% — зменшує роздільність вдвічі\n"
            "• FPS=0 — зберігає оригінальний FPS відео\n"
            "• Аудіодоріжка не переноситься у вихідний файл"
        ),
        'select_input': 'Виберіть вхідне відео',
        'select_output': 'Зберегти результат',
        'video_files': 'Відео файли', 'all_files': 'Всі файли',
        'warn_no_input': 'Виберіть вхідний файл!',
        'warn_no_output': 'Вкажіть вихідний файл!',
        'done_title': 'Завершено!',
        'done_msg': 'Обробку завершено за {t}.\n\nЕфект:   {eff}\nФайл:    {out}\nРозмір:  {sz}\nКадрів:  {fr}',
        'err_title': 'Помилка',
        'err_msg': 'Обробка завершилася з помилкою за {t}.\n\n{e}',
        'fx_pixelate': 'Пікселізація',
        'fx_wave':     'Хвилі',
        'fx_stripes':  'Смуги',
        'fx_glitch':   'Глітч',
        'fx_chromatic':'Хроматична аберація',
        'fx_scanlines':'Рядки (scanlines)',
        'fx_quantize': 'Квантизація кольору',
        'fx_vhs':      'VHS',
        'fx_rgb_shift':'RGB Зсув',
        'fx_mirror':   'Дзеркало',
        'fx_neon':     'Неон',
        'desc_pixelate': 'Ділить кадр на великі квадратні блоки — ретро-піксельна графіка.',
        'desc_wave':     'Вигинає рядки або стовпці синусоїдою — хвиля, що анімується з часом.',
        'desc_stripes':  'Накладає темні горизонтальні або вертикальні смуги — ефект жалюзі.',
        'desc_glitch':   'Випадково зсуває горизонтальні полоси та канали кольору — збій сигналу.',
        'desc_chromatic':'Розводить червоний і синій канали — веселкові краї, як у поганої оптики.',
        'desc_scanlines':'Затемнює кожен N-й рядок — ефект кінескопа старого телевізора.',
        'desc_quantize': 'Зменшує кількість колірних рівнів — постеризація, 8-бітна графіка.',
        'desc_vhs':      'Поєднує рядки, хроматику, шум і мерехтіння — зношена відеокасета.',
        'desc_rgb_shift':'Незалежно зсуває канали R, G, B — кольорові «привиди» навколо об\'єктів.',
        'desc_mirror':   'Копіює половину кадру і відображає — ідеально симетричне зображення.',
        'desc_neon':     'Виділяє краї та малює їх яскравими лініями, що світяться на темному тлі.',
        'p_block_size':   'Розмір блоку (px)',
        'p_amplitude':    'Амплітуда (px)',
        'p_frequency':    'Частота',
        'p_axis':         'Напрямок',
        'p_stripe_width': 'Ширина смуги (px)',
        'p_opacity':      'Прозорість (%)',
        'p_orientation':  'Орієнтація',
        'p_intensity':    'Інтенсивність',
        'p_block_height': 'Висота блоку (px)',
        'p_shift':        'Зсув каналів (px)',
        'p_line_gap':     'Крок рядка (px)',
        'p_darkness':     'Затемнення (%)',
        'p_colors':       'Кількість відтінків',
        'p_noise':        'Шум',
        'p_track_error':  'Зсув треку (px)',
        'p_r_shift':      'Зсув R (px)',
        'p_g_shift':      'Зсув G (px)',
        'p_b_shift':      'Зсув B (px)',
        'p_mode':         'Вісь',
        'p_blur':         'Розмиття свічення',
        'p_boost':        'Підсилення',
    },
    'de': {
        'process': 'Verarbeitung', 'settings': 'Einstellungen',
        'input_file': 'Eingabedatei:', 'output_file': 'Ausgabedatei (MP4):',
        'browse': 'Durchsuchen...', 'effect': 'Effekt:',
        'start': 'Verarbeitung starten', 'stop': 'Stopp', 'status': 'Status:',
        'ready': 'Bereit', 'processing': 'Verarbeitung...', 'done': 'Fertig!',
        'stopped': 'Gestoppt', 'error': 'Fehler',
        'params_lf': 'Effektparameter', 'info_lf': 'Informationen',
        'stat_elapsed': 'Vergangen:', 'stat_remaining': 'Verbleibend:',
        'stat_frame': 'Frame:', 'stat_fps': 'Quell-FPS:',
        'stat_res': 'Auflösung:', 'stat_size': 'Dateigröße:',
        'out_fps': 'Ausgabe-FPS:', 'out_fps_auto': '0 (auto)',
        'scale': 'Skalierung:', 'codec': 'Codec:',
        'hints_lf': 'Hinweise', 'language': 'Sprache:',
        'hints': (
            "• mp4v  — breite Kompatibilität, größere Datei\n"
            "• avc1  — H.264, bessere Kompression (erfordert ffmpeg)\n"
            "• Skalierung 50% — halbiert die Auflösung\n"
            "• FPS=0 — behält originale Video-FPS\n"
            "• Audiospur wird nicht in die Ausgabe kopiert"
        ),
        'select_input': 'Eingabevideo auswählen',
        'select_output': 'Ergebnis speichern',
        'video_files': 'Videodateien', 'all_files': 'Alle Dateien',
        'warn_no_input': 'Bitte Eingabedatei auswählen!',
        'warn_no_output': 'Bitte Ausgabedatei angeben!',
        'done_title': 'Abgeschlossen!',
        'done_msg': 'Verarbeitung abgeschlossen in {t}.\n\nEffekt:  {eff}\nDatei:   {out}\nGröße:   {sz}\nFrames:  {fr}',
        'err_title': 'Fehler',
        'err_msg': 'Verarbeitung fehlgeschlagen nach {t}.\n\n{e}',
        'fx_pixelate': 'Pixelierung',
        'fx_wave':     'Welle',
        'fx_stripes':  'Streifen',
        'fx_glitch':   'Glitch',
        'fx_chromatic':'Chromatische Aberration',
        'fx_scanlines':'Scanlines',
        'fx_quantize': 'Farbquantisierung',
        'fx_vhs':      'VHS',
        'fx_rgb_shift':'RGB-Verschiebung',
        'fx_mirror':   'Spiegel',
        'fx_neon':     'Neon',
        'desc_pixelate': 'Teilt das Bild in große Quadrate — Retro-Pixel-Art-Look.',
        'desc_wave':     'Verbiegt Zeilen oder Spalten mit einer Sinuswelle — animierte Wellenverzerrung.',
        'desc_stripes':  'Überlagert dunkle horizontale oder vertikale Bänder — wie Jalousien.',
        'desc_glitch':   'Verschiebt zufällig horizontale Streifen und Farbkanäle — korruptes Signal.',
        'desc_chromatic':'Trennt den roten und blauen Kanal seitlich — Regenbogenränder.',
        'desc_scanlines':'Verdunkelt jede N-te Zeile — CRT-Fernseheffekt.',
        'desc_quantize': 'Reduziert Farbstufen — posterisierter 8-Bit-Look.',
        'desc_vhs':      'Kombiniert Scanlines, Chromatik, Rauschen und Flackern — alte VHS-Kassette.',
        'desc_rgb_shift':'Verschiebt R-, G- und B-Kanäle unabhängig — farbige Geisterbilder.',
        'desc_mirror':   'Spiegelt eine Hälfte — perfekt symmetrisches Bild.',
        'desc_neon':     'Extrahiert Kanten und rendert sie als leuchtende Linien auf dunklem Hintergrund.',
        'p_block_size':   'Blockgröße (px)',
        'p_amplitude':    'Amplitude (px)',
        'p_frequency':    'Frequenz',
        'p_axis':         'Richtung',
        'p_stripe_width': 'Streifenbreite (px)',
        'p_opacity':      'Deckkraft (%)',
        'p_orientation':  'Ausrichtung',
        'p_intensity':    'Intensität',
        'p_block_height': 'Blockhöhe (px)',
        'p_shift':        'Kanalverschiebung (px)',
        'p_line_gap':     'Zeilenabstand (px)',
        'p_darkness':     'Dunkelheit (%)',
        'p_colors':       'Farbstufen',
        'p_noise':        'Rauschen',
        'p_track_error':  'Spurverschiebung (px)',
        'p_r_shift':      'R-Verschiebung (px)',
        'p_g_shift':      'G-Verschiebung (px)',
        'p_b_shift':      'B-Verschiebung (px)',
        'p_mode':         'Achse',
        'p_blur':         'Glühunschärfe',
        'p_boost':        'Verstärkung',
    },
    'fr': {
        'process': 'Traitement', 'settings': 'Paramètres',
        'input_file': "Fichier d'entrée:", 'output_file': 'Fichier de sortie (MP4):',
        'browse': 'Parcourir...', 'effect': 'Effet:',
        'start': 'Démarrer le traitement', 'stop': 'Arrêt', 'status': 'Statut:',
        'ready': 'Prêt', 'processing': 'Traitement...', 'done': 'Terminé!',
        'stopped': 'Arrêté', 'error': 'Erreur',
        'params_lf': "Paramètres de l'effet", 'info_lf': 'Informations',
        'stat_elapsed': 'Écoulé:', 'stat_remaining': 'Restant:',
        'stat_frame': 'Image:', 'stat_fps': 'FPS source:',
        'stat_res': 'Résolution:', 'stat_size': 'Taille fichier:',
        'out_fps': 'FPS sortie:', 'out_fps_auto': '0 (auto)',
        'scale': 'Échelle:', 'codec': 'Codec:',
        'hints_lf': 'Conseils', 'language': 'Langue:',
        'hints': (
            "• mp4v  — large compatibilité, fichier plus grand\n"
            "• avc1  — H.264, meilleure compression (nécessite ffmpeg)\n"
            "• Échelle 50% — réduit la résolution de moitié\n"
            "• FPS=0 — conserve le FPS original de la vidéo\n"
            "• La piste audio n'est pas copiée dans la sortie"
        ),
        'select_input': "Sélectionner la vidéo d'entrée",
        'select_output': 'Enregistrer le résultat',
        'video_files': 'Fichiers vidéo', 'all_files': 'Tous les fichiers',
        'warn_no_input': "Veuillez sélectionner un fichier d'entrée!",
        'warn_no_output': 'Veuillez spécifier un fichier de sortie!',
        'done_title': 'Terminé!',
        'done_msg': 'Traitement terminé en {t}.\n\nEffet:   {eff}\nFichier: {out}\nTaille:  {sz}\nImages:  {fr}',
        'err_title': 'Erreur',
        'err_msg': 'Traitement échoué après {t}.\n\n{e}',
        'fx_pixelate': 'Pixélisation',
        'fx_wave':     'Vague',
        'fx_stripes':  'Rayures',
        'fx_glitch':   'Glitch',
        'fx_chromatic':'Aberration chromatique',
        'fx_scanlines':'Lignes de balayage',
        'fx_quantize': 'Quantification couleur',
        'fx_vhs':      'VHS',
        'fx_rgb_shift':'Décalage RVB',
        'fx_mirror':   'Miroir',
        'fx_neon':     'Néon',
        'desc_pixelate': 'Divise le cadre en grands carrés — look pixel-art rétro.',
        'desc_wave':     'Courbe les lignes ou colonnes avec une sinusoïde — distorsion animée.',
        'desc_stripes':  'Superpose des bandes sombres horizontales ou verticales — effet jalousie.',
        'desc_glitch':   'Décale aléatoirement des bandes horizontales et des canaux — signal corrompu.',
        'desc_chromatic':'Sépare les canaux rouge et bleu — halos arc-en-ciel sur les bords.',
        'desc_scanlines':'Assombrit chaque N-ième ligne — effet écran cathodique.',
        'desc_quantize': 'Réduit les niveaux de couleur — look 8 bits posterisé.',
        'desc_vhs':      'Combine lignes, chromatique, bruit et scintillement — vieille cassette VHS.',
        'desc_rgb_shift':'Décale indépendamment R, V et B — fantômes colorés.',
        'desc_mirror':   'Copie et retourne la moitié du cadre — image parfaitement symétrique.',
        'desc_neon':     'Extrait les contours et les rend comme des lignes lumineuses sur fond sombre.',
        'p_block_size':   'Taille du bloc (px)',
        'p_amplitude':    'Amplitude (px)',
        'p_frequency':    'Fréquence',
        'p_axis':         'Direction',
        'p_stripe_width': 'Largeur de rayure (px)',
        'p_opacity':      'Opacité (%)',
        'p_orientation':  'Orientation',
        'p_intensity':    'Intensité',
        'p_block_height': 'Hauteur du bloc (px)',
        'p_shift':        'Décalage de canal (px)',
        'p_line_gap':     'Espacement ligne (px)',
        'p_darkness':     'Obscurité (%)',
        'p_colors':       'Niveaux de couleur',
        'p_noise':        'Bruit',
        'p_track_error':  'Erreur de piste (px)',
        'p_r_shift':      'Décalage R (px)',
        'p_g_shift':      'Décalage V (px)',
        'p_b_shift':      'Décalage B (px)',
        'p_mode':         'Axe',
        'p_blur':         'Flou de halo',
        'p_boost':        'Amplification',
    },
    'es': {
        'process': 'Procesar', 'settings': 'Configuración',
        'input_file': 'Archivo de entrada:', 'output_file': 'Archivo de salida (MP4):',
        'browse': 'Examinar...', 'effect': 'Efecto:',
        'start': 'Iniciar procesamiento', 'stop': 'Detener', 'status': 'Estado:',
        'ready': 'Listo', 'processing': 'Procesando...', 'done': '¡Completado!',
        'stopped': 'Detenido', 'error': 'Error',
        'params_lf': 'Parámetros del efecto', 'info_lf': 'Información',
        'stat_elapsed': 'Transcurrido:', 'stat_remaining': 'Restante:',
        'stat_frame': 'Fotograma:', 'stat_fps': 'FPS fuente:',
        'stat_res': 'Resolución:', 'stat_size': 'Tamaño archivo:',
        'out_fps': 'FPS salida:', 'out_fps_auto': '0 (auto)',
        'scale': 'Escala:', 'codec': 'Códec:',
        'hints_lf': 'Consejos', 'language': 'Idioma:',
        'hints': (
            "• mp4v  — amplia compatibilidad, archivo mayor\n"
            "• avc1  — H.264, mejor compresión (requiere ffmpeg)\n"
            "• Escala 50% — reduce la resolución a la mitad\n"
            "• FPS=0 — conserva los FPS originales del vídeo\n"
            "• La pista de audio no se copia en la salida"
        ),
        'select_input': 'Seleccionar vídeo de entrada',
        'select_output': 'Guardar resultado',
        'video_files': 'Archivos de vídeo', 'all_files': 'Todos los archivos',
        'warn_no_input': '¡Seleccione un archivo de entrada!',
        'warn_no_output': '¡Especifique un archivo de salida!',
        'done_title': '¡Completado!',
        'done_msg': 'Procesamiento completado en {t}.\n\nEfecto:  {eff}\nArchivo: {out}\nTamaño:  {sz}\nFotos:   {fr}',
        'err_title': 'Error',
        'err_msg': 'Procesamiento fallido tras {t}.\n\n{e}',
        'fx_pixelate': 'Pixelado',
        'fx_wave':     'Onda',
        'fx_stripes':  'Franjas',
        'fx_glitch':   'Glitch',
        'fx_chromatic':'Aberración cromática',
        'fx_scanlines':'Líneas de exploración',
        'fx_quantize': 'Cuantización de color',
        'fx_vhs':      'VHS',
        'fx_rgb_shift':'Desplazamiento RGB',
        'fx_mirror':   'Espejo',
        'fx_neon':     'Neón',
        'desc_pixelate': 'Divide el fotograma en grandes cuadrados — look de píxel-art retro.',
        'desc_wave':     'Curva filas o columnas con una sinusoide — distorsión de ola animada.',
        'desc_stripes':  'Superpone bandas oscuras horizontales o verticales — efecto persiana.',
        'desc_glitch':   'Desplaza aleatoriamente franjas horizontales y canales de color — señal corrupta.',
        'desc_chromatic':'Separa los canales rojo y azul — halos de arcoíris en los bordes.',
        'desc_scanlines':'Oscurece cada N-ésima línea — efecto de pantalla CRT.',
        'desc_quantize': 'Reduce los niveles de color — look posterizado de 8 bits.',
        'desc_vhs':      'Combina líneas, cromática, ruido y parpadeo — viejo casete VHS.',
        'desc_rgb_shift':'Desplaza R, G y B independientemente — fantasmas de colores.',
        'desc_mirror':   'Copia y voltea la mitad del fotograma — imagen perfectamente simétrica.',
        'desc_neon':     'Extrae bordes y los renderiza como líneas luminosas sobre fondo oscuro.',
        'p_block_size':   'Tamaño de bloque (px)',
        'p_amplitude':    'Amplitud (px)',
        'p_frequency':    'Frecuencia',
        'p_axis':         'Dirección',
        'p_stripe_width': 'Anchura de franja (px)',
        'p_opacity':      'Opacidad (%)',
        'p_orientation':  'Orientación',
        'p_intensity':    'Intensidad',
        'p_block_height': 'Altura de bloque (px)',
        'p_shift':        'Desplazamiento de canal (px)',
        'p_line_gap':     'Paso de línea (px)',
        'p_darkness':     'Oscuridad (%)',
        'p_colors':       'Niveles de color',
        'p_noise':        'Ruido',
        'p_track_error':  'Error de pista (px)',
        'p_r_shift':      'Desp. R (px)',
        'p_g_shift':      'Desp. G (px)',
        'p_b_shift':      'Desp. B (px)',
        'p_mode':         'Eje',
        'p_blur':         'Desenfoque de brillo',
        'p_boost':        'Amplificación',
    },
    'pl': {
        'process': 'Przetwarzanie', 'settings': 'Ustawienia',
        'input_file': 'Plik wejściowy:', 'output_file': 'Plik wyjściowy (MP4):',
        'browse': 'Przeglądaj...', 'effect': 'Efekt:',
        'start': 'Rozpocznij przetwarzanie', 'stop': 'Stop', 'status': 'Status:',
        'ready': 'Gotowe', 'processing': 'Przetwarzanie...', 'done': 'Gotowe!',
        'stopped': 'Zatrzymano', 'error': 'Błąd',
        'params_lf': 'Parametry efektu', 'info_lf': 'Informacje',
        'stat_elapsed': 'Upłynęło:', 'stat_remaining': 'Pozostało:',
        'stat_frame': 'Klatka:', 'stat_fps': 'FPS źródła:',
        'stat_res': 'Rozdzielczość:', 'stat_size': 'Rozmiar pliku:',
        'out_fps': 'Wyjściowy FPS:', 'out_fps_auto': '0 (auto)',
        'scale': 'Skala:', 'codec': 'Kodek:',
        'hints_lf': 'Wskazówki', 'language': 'Język:',
        'hints': (
            "• mp4v  — szeroka zgodność, większy plik\n"
            "• avc1  — H.264, lepsze kompresja (wymaga ffmpeg)\n"
            "• Skala 50% — zmniejsza rozdzielczość o połowę\n"
            "• FPS=0 — zachowuje oryginalny FPS wideo\n"
            "• Ścieżka audio nie jest kopiowana do wyjścia"
        ),
        'select_input': 'Wybierz wejściowy plik wideo',
        'select_output': 'Zapisz wynik',
        'video_files': 'Pliki wideo', 'all_files': 'Wszystkie pliki',
        'warn_no_input': 'Wybierz plik wejściowy!',
        'warn_no_output': 'Podaj plik wyjściowy!',
        'done_title': 'Gotowe!',
        'done_msg': 'Przetwarzanie zakończone w {t}.\n\nEfekt:   {eff}\nPlik:    {out}\nRozmiar: {sz}\nKlatki:  {fr}',
        'err_title': 'Błąd',
        'err_msg': 'Przetwarzanie nieudane po {t}.\n\n{e}',
        'fx_pixelate': 'Pikselizacja',
        'fx_wave':     'Fala',
        'fx_stripes':  'Paski',
        'fx_glitch':   'Glitch',
        'fx_chromatic':'Aberracja chromatyczna',
        'fx_scanlines':'Linie skanowania',
        'fx_quantize': 'Kwantyzacja koloru',
        'fx_vhs':      'VHS',
        'fx_rgb_shift':'Przesunięcie RGB',
        'fx_mirror':   'Lustro',
        'fx_neon':     'Neon',
        'desc_pixelate': 'Dzieli klatkę na duże kwadraty — retro pixel-art.',
        'desc_wave':     'Zgina wiersze lub kolumny sinusoidą — animowane falowe zniekształcenie.',
        'desc_stripes':  'Nakłada ciemne poziome lub pionowe paski — efekt żaluzji.',
        'desc_glitch':   'Losowo przesuwa poziome paski i kanały kolorów — uszkodzony sygnał.',
        'desc_chromatic':'Rozdziela czerwony i niebieski kanał — tęczowe krawędzie.',
        'desc_scanlines':'Przyciemnia co N-tą linię — efekt monitora CRT.',
        'desc_quantize': 'Zmniejsza poziomy kolorów — posteryzowany wygląd 8-bitowy.',
        'desc_vhs':      'Łączy linie, chromatykę, szum i migotanie — stara kaseta VHS.',
        'desc_rgb_shift':'Przesuwa R, G i B niezależnie — kolorowe duchy.',
        'desc_mirror':   'Kopiuje i odwraca połowę klatki — idealnie symetryczny obraz.',
        'desc_neon':     'Wyodrębnia krawędzie i renderuje je jako świecące linie na ciemnym tle.',
        'p_block_size':   'Rozmiar bloku (px)',
        'p_amplitude':    'Amplituda (px)',
        'p_frequency':    'Częstotliwość',
        'p_axis':         'Kierunek',
        'p_stripe_width': 'Szerokość paska (px)',
        'p_opacity':      'Krycie (%)',
        'p_orientation':  'Orientacja',
        'p_intensity':    'Intensywność',
        'p_block_height': 'Wysokość bloku (px)',
        'p_shift':        'Przesunięcie kanału (px)',
        'p_line_gap':     'Odstęp linii (px)',
        'p_darkness':     'Ciemność (%)',
        'p_colors':       'Poziomy kolorów',
        'p_noise':        'Szum',
        'p_track_error':  'Błąd ścieżki (px)',
        'p_r_shift':      'Przesunięcie R (px)',
        'p_g_shift':      'Przesunięcie G (px)',
        'p_b_shift':      'Przesunięcie B (px)',
        'p_mode':         'Oś',
        'p_blur':         'Rozmycie świecenia',
        'p_boost':        'Wzmocnienie',
    },
    'pt': {
        'process': 'Processar', 'settings': 'Configurações',
        'input_file': 'Arquivo de entrada:', 'output_file': 'Arquivo de saída (MP4):',
        'browse': 'Procurar...', 'effect': 'Efeito:',
        'start': 'Iniciar processamento', 'stop': 'Parar', 'status': 'Status:',
        'ready': 'Pronto', 'processing': 'Processando...', 'done': 'Concluído!',
        'stopped': 'Parado', 'error': 'Erro',
        'params_lf': 'Parâmetros do efeito', 'info_lf': 'Informações',
        'stat_elapsed': 'Decorrido:', 'stat_remaining': 'Restante:',
        'stat_frame': 'Quadro:', 'stat_fps': 'FPS fonte:',
        'stat_res': 'Resolução:', 'stat_size': 'Tamanho arquivo:',
        'out_fps': 'FPS saída:', 'out_fps_auto': '0 (auto)',
        'scale': 'Escala:', 'codec': 'Codec:',
        'hints_lf': 'Dicas', 'language': 'Idioma:',
        'hints': (
            "• mp4v  — ampla compatibilidade, arquivo maior\n"
            "• avc1  — H.264, melhor compressão (requer ffmpeg)\n"
            "• Escala 50% — reduz a resolução à metade\n"
            "• FPS=0 — mantém o FPS original do vídeo\n"
            "• A faixa de áudio não é copiada para a saída"
        ),
        'select_input': 'Selecionar vídeo de entrada',
        'select_output': 'Salvar resultado',
        'video_files': 'Arquivos de vídeo', 'all_files': 'Todos os arquivos',
        'warn_no_input': 'Selecione um arquivo de entrada!',
        'warn_no_output': 'Especifique um arquivo de saída!',
        'done_title': 'Concluído!',
        'done_msg': 'Processamento concluído em {t}.\n\nEfeito:  {eff}\nArquivo: {out}\nTamanho: {sz}\nQuadros: {fr}',
        'err_title': 'Erro',
        'err_msg': 'Processamento falhou após {t}.\n\n{e}',
        'fx_pixelate': 'Pixelização',
        'fx_wave':     'Onda',
        'fx_stripes':  'Listras',
        'fx_glitch':   'Glitch',
        'fx_chromatic':'Aberração cromática',
        'fx_scanlines':'Linhas de varredura',
        'fx_quantize': 'Quantização de cor',
        'fx_vhs':      'VHS',
        'fx_rgb_shift':'Deslocamento RGB',
        'fx_mirror':   'Espelho',
        'fx_neon':     'Neon',
        'desc_pixelate': 'Divide o quadro em grandes quadrados — visual pixel-art retrô.',
        'desc_wave':     'Curva linhas ou colunas com uma sinusoide — distorção de onda animada.',
        'desc_stripes':  'Sobrepõe faixas escuras horizontais ou verticais — efeito persiana.',
        'desc_glitch':   'Desloca aleatoriamente faixas horizontais e canais de cor — sinal corrompido.',
        'desc_chromatic':'Separa os canais vermelho e azul — halos de arco-íris nas bordas.',
        'desc_scanlines':'Escurece cada N-ésima linha — efeito de monitor CRT.',
        'desc_quantize': 'Reduz os níveis de cor — visual posterizado de 8 bits.',
        'desc_vhs':      'Combina linhas, cromática, ruído e cintilação — velha fita VHS.',
        'desc_rgb_shift':'Desloca R, G e B independentemente — fantasmas coloridos.',
        'desc_mirror':   'Copia e vira metade do quadro — imagem perfeitamente simétrica.',
        'desc_neon':     'Extrai bordas e as renderiza como linhas brilhantes sobre fundo escuro.',
        'p_block_size':   'Tamanho do bloco (px)',
        'p_amplitude':    'Amplitude (px)',
        'p_frequency':    'Frequência',
        'p_axis':         'Direção',
        'p_stripe_width': 'Largura da listra (px)',
        'p_opacity':      'Opacidade (%)',
        'p_orientation':  'Orientação',
        'p_intensity':    'Intensidade',
        'p_block_height': 'Altura do bloco (px)',
        'p_shift':        'Deslocamento de canal (px)',
        'p_line_gap':     'Espaçamento de linha (px)',
        'p_darkness':     'Escuridão (%)',
        'p_colors':       'Níveis de cor',
        'p_noise':        'Ruído',
        'p_track_error':  'Erro de trilha (px)',
        'p_r_shift':      'Desl. R (px)',
        'p_g_shift':      'Desl. G (px)',
        'p_b_shift':      'Desl. B (px)',
        'p_mode':         'Eixo',
        'p_blur':         'Desfoque de brilho',
        'p_boost':        'Amplificação',
    },
    'it': {
        'process': 'Elaborazione', 'settings': 'Impostazioni',
        'input_file': 'File di input:', 'output_file': 'File di output (MP4):',
        'browse': 'Sfoglia...', 'effect': 'Effetto:',
        'start': "Avvia elaborazione", 'stop': 'Stop', 'status': 'Stato:',
        'ready': 'Pronto', 'processing': 'Elaborazione...', 'done': 'Completato!',
        'stopped': 'Fermato', 'error': 'Errore',
        'params_lf': "Parametri dell'effetto", 'info_lf': 'Informazioni',
        'stat_elapsed': 'Trascorso:', 'stat_remaining': 'Rimanente:',
        'stat_frame': 'Frame:', 'stat_fps': 'FPS sorgente:',
        'stat_res': 'Risoluzione:', 'stat_size': 'Dim. file:',
        'out_fps': 'FPS uscita:', 'out_fps_auto': '0 (auto)',
        'scale': 'Scala:', 'codec': 'Codec:',
        'hints_lf': 'Suggerimenti', 'language': 'Lingua:',
        'hints': (
            "• mp4v  — ampia compatibilità, file più grande\n"
            "• avc1  — H.264, migliore compressione (richiede ffmpeg)\n"
            "• Scala 50% — dimezza la risoluzione\n"
            "• FPS=0 — mantiene i FPS originali del video\n"
            "• La traccia audio non viene copiata nell'output"
        ),
        'select_input': 'Seleziona video di input',
        'select_output': 'Salva risultato',
        'video_files': 'File video', 'all_files': 'Tutti i file',
        'warn_no_input': 'Seleziona un file di input!',
        'warn_no_output': 'Specifica un file di output!',
        'done_title': 'Completato!',
        'done_msg': 'Elaborazione completata in {t}.\n\nEffetto: {eff}\nFile:    {out}\nDim.:    {sz}\nFrame:   {fr}',
        'err_title': 'Errore',
        'err_msg': 'Elaborazione fallita dopo {t}.\n\n{e}',
        'fx_pixelate': 'Pixelizzazione',
        'fx_wave':     'Onda',
        'fx_stripes':  'Strisce',
        'fx_glitch':   'Glitch',
        'fx_chromatic':'Aberrazione cromatica',
        'fx_scanlines':'Linee di scansione',
        'fx_quantize': 'Quantizzazione colore',
        'fx_vhs':      'VHS',
        'fx_rgb_shift':'Spostamento RGB',
        'fx_mirror':   'Specchio',
        'fx_neon':     'Neon',
        'desc_pixelate': 'Divide il frame in grandi quadrati — look pixel-art retrò.',
        'desc_wave':     'Piega righe o colonne con una sinusoide — distorsione a onda animata.',
        'desc_stripes':  'Sovrappone bande scure orizzontali o verticali — effetto veneziana.',
        'desc_glitch':   'Sposta casualmente strisce orizzontali e canali di colore — segnale corrotto.',
        'desc_chromatic':'Separa i canali rosso e blu — aloni arcobaleno sui bordi.',
        'desc_scanlines':'Scurisce ogni N-esima riga — effetto monitor CRT.',
        'desc_quantize': 'Riduce i livelli di colore — look posterizzato a 8 bit.',
        'desc_vhs':      'Combina linee, cromatica, rumore e sfarfallio — vecchia cassetta VHS.',
        'desc_rgb_shift':'Sposta R, G e B indipendentemente — fantasmi colorati.',
        'desc_mirror':   'Copia e capovolge metà del frame — immagine perfettamente simmetrica.',
        'desc_neon':     'Estrae i bordi e li renderizza come linee luminose su sfondo scuro.',
        'p_block_size':   'Dim. blocco (px)',
        'p_amplitude':    'Ampiezza (px)',
        'p_frequency':    'Frequenza',
        'p_axis':         'Direzione',
        'p_stripe_width': 'Larghezza striscia (px)',
        'p_opacity':      'Opacità (%)',
        'p_orientation':  'Orientamento',
        'p_intensity':    'Intensità',
        'p_block_height': 'Altezza blocco (px)',
        'p_shift':        'Spostamento canale (px)',
        'p_line_gap':     'Passo riga (px)',
        'p_darkness':     'Oscurità (%)',
        'p_colors':       'Livelli colore',
        'p_noise':        'Rumore',
        'p_track_error':  'Errore traccia (px)',
        'p_r_shift':      'Spost. R (px)',
        'p_g_shift':      'Spost. G (px)',
        'p_b_shift':      'Spost. B (px)',
        'p_mode':         'Asse',
        'p_blur':         'Sfocatura bagliore',
        'p_boost':        'Amplificazione',
    },
    'zh': {
        'process': '处理', 'settings': '设置',
        'input_file': '输入文件：', 'output_file': '输出文件（MP4）：',
        'browse': '浏览...', 'effect': '效果：',
        'start': '开始处理', 'stop': '停止', 'status': '状态：',
        'ready': '就绪', 'processing': '处理中...', 'done': '完成！',
        'stopped': '已停止', 'error': '错误',
        'params_lf': '效果参数', 'info_lf': '信息',
        'stat_elapsed': '已用时：', 'stat_remaining': '剩余：',
        'stat_frame': '帧：', 'stat_fps': '源FPS：',
        'stat_res': '分辨率：', 'stat_size': '文件大小：',
        'out_fps': '输出FPS：', 'out_fps_auto': '0（自动）',
        'scale': '缩放：', 'codec': '编解码器：',
        'hints_lf': '提示', 'language': '语言：',
        'hints': (
            "• mp4v  — 广泛兼容，文件较大\n"
            "• avc1  — H.264，更好压缩（需要ffmpeg）\n"
            "• 缩放50% — 将分辨率减半\n"
            "• FPS=0 — 保持原始视频FPS\n"
            "• 音频轨道不会复制到输出"
        ),
        'select_input': '选择输入视频',
        'select_output': '保存结果',
        'video_files': '视频文件', 'all_files': '所有文件',
        'warn_no_input': '请选择输入文件！',
        'warn_no_output': '请指定输出文件！',
        'done_title': '完成！',
        'done_msg': '处理完成，用时 {t}。\n\n效果：   {eff}\n文件：   {out}\n大小：   {sz}\n帧数：   {fr}',
        'err_title': '错误',
        'err_msg': '处理失败，用时 {t}。\n\n{e}',
        'fx_pixelate': '像素化',
        'fx_wave':     '波浪',
        'fx_stripes':  '条纹',
        'fx_glitch':   '故障',
        'fx_chromatic':'色差',
        'fx_scanlines':'扫描线',
        'fx_quantize': '色彩量化',
        'fx_vhs':      'VHS',
        'fx_rgb_shift':'RGB偏移',
        'fx_mirror':   '镜像',
        'fx_neon':     '霓虹',
        'desc_pixelate': '将帧分割为大方块——复古像素艺术风格。',
        'desc_wave':     '用正弦波弯曲行或列——随时间变化的波纹失真。',
        'desc_stripes':  '叠加深色水平或垂直条纹——百叶窗效果。',
        'desc_glitch':   '随机移动水平条和颜色通道——模拟数字信号损坏。',
        'desc_chromatic':'横向分离红蓝通道——边缘出现彩虹光晕。',
        'desc_scanlines':'每隔N行变暗——模拟CRT显示器效果。',
        'desc_quantize': '减少颜色级别——海报化8位风格。',
        'desc_vhs':      '组合扫描线、色差、噪点和闪烁——旧VHS磁带效果。',
        'desc_rgb_shift':'独立偏移R、G、B通道——彩色重影效果。',
        'desc_mirror':   '复制并翻转一半帧——完全对称的图像。',
        'desc_neon':     '提取边缘并在暗背景上渲染为发光线条。',
        'p_block_size':   '块大小（px）',
        'p_amplitude':    '振幅（px）',
        'p_frequency':    '频率',
        'p_axis':         '方向',
        'p_stripe_width': '条纹宽度（px）',
        'p_opacity':      '不透明度（%）',
        'p_orientation':  '方向',
        'p_intensity':    '强度',
        'p_block_height': '块高度（px）',
        'p_shift':        '通道偏移（px）',
        'p_line_gap':     '行间距（px）',
        'p_darkness':     '暗度（%）',
        'p_colors':       '颜色级别',
        'p_noise':        '噪点',
        'p_track_error':  '磁轨偏移（px）',
        'p_r_shift':      'R偏移（px）',
        'p_g_shift':      'G偏移（px）',
        'p_b_shift':      'B偏移（px）',
        'p_mode':         '轴',
        'p_blur':         '光晕模糊',
        'p_boost':        '增强',
    },
    'ja': {
        'process': '処理', 'settings': '設定',
        'input_file': '入力ファイル：', 'output_file': '出力ファイル（MP4）：',
        'browse': '参照...', 'effect': 'エフェクト：',
        'start': '処理を開始', 'stop': '停止', 'status': 'ステータス：',
        'ready': '準備完了', 'processing': '処理中...', 'done': '完了！',
        'stopped': '停止しました', 'error': 'エラー',
        'params_lf': 'エフェクトパラメータ', 'info_lf': '情報',
        'stat_elapsed': '経過：', 'stat_remaining': '残り：',
        'stat_frame': 'フレーム：', 'stat_fps': 'ソースFPS：',
        'stat_res': '解像度：', 'stat_size': 'ファイルサイズ：',
        'out_fps': '出力FPS：', 'out_fps_auto': '0（自動）',
        'scale': 'スケール：', 'codec': 'コーデック：',
        'hints_lf': 'ヒント', 'language': '言語：',
        'hints': (
            "• mp4v  — 幅広い互換性、ファイルサイズ大\n"
            "• avc1  — H.264、高圧縮（ffmpeg必要）\n"
            "• スケール50% — 解像度を半分にする\n"
            "• FPS=0 — 元のFPSを維持する\n"
            "• 音声トラックは出力にコピーされません"
        ),
        'select_input': '入力動画を選択',
        'select_output': '結果を保存',
        'video_files': '動画ファイル', 'all_files': 'すべてのファイル',
        'warn_no_input': '入力ファイルを選択してください！',
        'warn_no_output': '出力ファイルを指定してください！',
        'done_title': '完了！',
        'done_msg': '処理が{t}で完了しました。\n\nエフェクト：{eff}\nファイル：{out}\nサイズ：{sz}\nフレーム：{fr}',
        'err_title': 'エラー',
        'err_msg': '処理が{t}後に失敗しました。\n\n{e}',
        'fx_pixelate': 'ピクセル化',
        'fx_wave':     '波',
        'fx_stripes':  'ストライプ',
        'fx_glitch':   'グリッチ',
        'fx_chromatic':'色収差',
        'fx_scanlines':'スキャンライン',
        'fx_quantize': 'カラー量子化',
        'fx_vhs':      'VHS',
        'fx_rgb_shift':'RGBシフト',
        'fx_mirror':   'ミラー',
        'fx_neon':     'ネオン',
        'desc_pixelate': 'フレームを大きな正方形に分割——レトロなピクセルアート。',
        'desc_wave':     '正弦波で行または列を曲げる——時間とともに動く波紋。',
        'desc_stripes':  '暗い水平または垂直の帯を重ねる——ブラインド効果。',
        'desc_glitch':   '水平スライスとカラーチャンネルをランダムにシフト——破損した信号。',
        'desc_chromatic':'赤と青のチャンネルを横方向に分離——エッジに虹色のフリンジ。',
        'desc_scanlines':'N行ごとに暗くする——CRTテレビ効果。',
        'desc_quantize': 'カラーレベルを削減——ポスタリゼーション8ビット風。',
        'desc_vhs':      'スキャンライン、色収差、ノイズ、ちらつきを組み合わせ——古いVHSテープ。',
        'desc_rgb_shift':'R、G、Bチャンネルを独立してシフト——カラーゴースト。',
        'desc_mirror':   '半分をコピーして反転——完全に対称な画像。',
        'desc_neon':     'エッジを抽出し暗い背景に光る線として描画。',
        'p_block_size':   'ブロックサイズ（px）',
        'p_amplitude':    '振幅（px）',
        'p_frequency':    '周波数',
        'p_axis':         '方向',
        'p_stripe_width': 'ストライプ幅（px）',
        'p_opacity':      '不透明度（%）',
        'p_orientation':  '向き',
        'p_intensity':    '強度',
        'p_block_height': 'ブロック高（px）',
        'p_shift':        'チャンネルシフト（px）',
        'p_line_gap':     'ライン間隔（px）',
        'p_darkness':     '暗さ（%）',
        'p_colors':       'カラーレベル',
        'p_noise':        'ノイズ',
        'p_track_error':  'トラックエラー（px）',
        'p_r_shift':      'Rシフト（px）',
        'p_g_shift':      'Gシフト（px）',
        'p_b_shift':      'Bシフト（px）',
        'p_mode':         '軸',
        'p_blur':         'グローブラー',
        'p_boost':        'ブースト',
    },
    'ko': {
        'process': '처리', 'settings': '설정',
        'input_file': '입력 파일:', 'output_file': '출력 파일 (MP4):',
        'browse': '찾아보기...', 'effect': '효과:',
        'start': '처리 시작', 'stop': '정지', 'status': '상태:',
        'ready': '준비', 'processing': '처리 중...', 'done': '완료!',
        'stopped': '중지됨', 'error': '오류',
        'params_lf': '효과 매개변수', 'info_lf': '정보',
        'stat_elapsed': '경과:', 'stat_remaining': '남은 시간:',
        'stat_frame': '프레임:', 'stat_fps': '소스 FPS:',
        'stat_res': '해상도:', 'stat_size': '파일 크기:',
        'out_fps': '출력 FPS:', 'out_fps_auto': '0 (자동)',
        'scale': '크기 조정:', 'codec': '코덱:',
        'hints_lf': '도움말', 'language': '언어:',
        'hints': (
            "• mp4v  — 광범위한 호환성, 파일 크기 큼\n"
            "• avc1  — H.264, 더 나은 압축 (ffmpeg 필요)\n"
            "• 크기 50% — 해상도를 절반으로 줄임\n"
            "• FPS=0 — 원본 비디오 FPS 유지\n"
            "• 오디오 트랙은 출력에 복사되지 않음"
        ),
        'select_input': '입력 비디오 선택',
        'select_output': '결과 저장',
        'video_files': '비디오 파일', 'all_files': '모든 파일',
        'warn_no_input': '입력 파일을 선택하세요!',
        'warn_no_output': '출력 파일을 지정하세요!',
        'done_title': '완료!',
        'done_msg': '처리 완료 ({t}).\n\n효과:    {eff}\n파일:    {out}\n크기:    {sz}\n프레임:  {fr}',
        'err_title': '오류',
        'err_msg': '처리 실패 ({t}).\n\n{e}',
        'fx_pixelate': '픽셀화',
        'fx_wave':     '파도',
        'fx_stripes':  '줄무늬',
        'fx_glitch':   '글리치',
        'fx_chromatic':'색수차',
        'fx_scanlines':'주사선',
        'fx_quantize': '색상 양자화',
        'fx_vhs':      'VHS',
        'fx_rgb_shift':'RGB 이동',
        'fx_mirror':   '거울',
        'fx_neon':     '네온',
        'desc_pixelate': '프레임을 큰 정사각형으로 분할 — 복고풍 픽셀 아트.',
        'desc_wave':     '사인파로 행 또는 열을 구부림 — 시간에 따라 움직이는 물결.',
        'desc_stripes':  '어두운 수평 또는 수직 띠를 겹침 — 블라인드 효과.',
        'desc_glitch':   '수평 슬라이스와 색상 채널을 무작위로 이동 — 손상된 신호.',
        'desc_chromatic':'적색과 청색 채널을 옆으로 분리 — 가장자리의 무지개 띠.',
        'desc_scanlines':'N번째 줄마다 어둡게 — CRT 텔레비전 효과.',
        'desc_quantize': '색상 레벨 감소 — 포스터화된 8비트 스타일.',
        'desc_vhs':      '주사선, 색수차, 노이즈, 깜박임 조합 — 낡은 VHS 테이프.',
        'desc_rgb_shift':'R, G, B 채널을 독립적으로 이동 — 색상 고스트.',
        'desc_mirror':   '절반을 복사하고 뒤집음 — 완전히 대칭적인 이미지.',
        'desc_neon':     '가장자리를 추출하여 어두운 배경에 빛나는 선으로 렌더링.',
        'p_block_size':   '블록 크기 (px)',
        'p_amplitude':    '진폭 (px)',
        'p_frequency':    '주파수',
        'p_axis':         '방향',
        'p_stripe_width': '줄무늬 너비 (px)',
        'p_opacity':      '불투명도 (%)',
        'p_orientation':  '방향',
        'p_intensity':    '강도',
        'p_block_height': '블록 높이 (px)',
        'p_shift':        '채널 이동 (px)',
        'p_line_gap':     '줄 간격 (px)',
        'p_darkness':     '어둡기 (%)',
        'p_colors':       '색상 레벨',
        'p_noise':        '노이즈',
        'p_track_error':  '트랙 오류 (px)',
        'p_r_shift':      'R 이동 (px)',
        'p_g_shift':      'G 이동 (px)',
        'p_b_shift':      'B 이동 (px)',
        'p_mode':         '축',
        'p_blur':         '글로우 블러',
        'p_boost':        '부스트',
    },
}

LANGUAGE_NAMES = {
    'en': 'English', 'ru': 'Русский', 'uk': 'Українська',
    'de': 'Deutsch', 'fr': 'Français', 'es': 'Español',
    'pl': 'Polski',  'pt': 'Português', 'it': 'Italiano',
    'zh': '中文',    'ja': '日本語',    'ko': '한국어',
}
LANG_ORDER = ['en', 'ru', 'uk', 'de', 'fr', 'es', 'pl', 'pt', 'it', 'zh', 'ja', 'ko']


# ─────────────────────────────────────────────────────────────────────────────
# EFFECTS ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def fx_pixelate(frame, block_size=16, **kw):
    h, w = frame.shape[:2]
    bs = max(1, int(block_size))
    s = cv2.resize(frame, (max(1, w // bs), max(1, h // bs)), interpolation=cv2.INTER_LINEAR)
    return cv2.resize(s, (w, h), interpolation=cv2.INTER_NEAREST)

def fx_wave(frame, amplitude=20, frequency=5, axis='horizontal', frame_idx=0, **kw):
    h, w = frame.shape[:2]
    phase = frame_idx * 0.15
    freq = float(frequency) * 0.01
    if axis == 'horizontal':
        ys = np.arange(h, dtype=np.float32)
        offsets = (float(amplitude) * np.sin(freq * ys + phase)).astype(np.int32)
        map_x = np.clip(np.arange(w, dtype=np.float32)[np.newaxis, :] + offsets[:, np.newaxis], 0, w-1).astype(np.float32)
        map_y = np.tile(ys[:, np.newaxis], (1, w)).astype(np.float32)
    else:
        xs = np.arange(w, dtype=np.float32)
        offsets = (float(amplitude) * np.sin(freq * xs + phase)).astype(np.int32)
        map_y = np.clip(np.arange(h, dtype=np.float32)[:, np.newaxis] + offsets[np.newaxis, :], 0, h-1).astype(np.float32)
        map_x = np.tile(xs[np.newaxis, :], (h, 1)).astype(np.float32)
    return cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def fx_stripes(frame, stripe_width=10, opacity=60, orientation='horizontal', **kw):
    overlay = frame.copy()
    h, w = frame.shape[:2]
    sw = max(1, int(stripe_width))
    op = float(opacity) * 0.01
    if orientation == 'horizontal':
        for y in range(0, h, sw * 2):
            overlay[y:y+sw] = 0
    else:
        for x in range(0, w, sw * 2):
            overlay[:, x:x+sw] = 0
    return cv2.addWeighted(overlay, op, frame, 1.0 - op, 0)

def fx_glitch(frame, intensity=8, block_height=20, frame_idx=0, **kw):
    rng = np.random.default_rng(frame_idx)
    result = frame.copy()
    h, w = frame.shape[:2]
    bh = max(1, int(block_height))
    inten = max(1, int(intensity))
    for i in range(h // bh):
        if rng.random() < 0.15:
            y1, y2 = i * bh, min((i+1) * bh, h)
            shift = int(rng.integers(-inten * 4, inten * 4 + 1))
            if shift:
                result[y1:y2] = np.roll(result[y1:y2], shift, axis=1)
    if rng.random() < 0.3:
        s = max(1, int(rng.integers(1, inten + 1)))
        result[:, :, 0] = np.roll(result[:, :, 0], s, axis=1)
        result[:, :, 2] = np.roll(result[:, :, 2], -s, axis=1)
    return result

def fx_chromatic(frame, shift=6, **kw):
    sh = max(0, int(shift))
    if sh == 0:
        return frame
    b, g, r = cv2.split(frame)
    return cv2.merge([np.roll(b, -sh, axis=1), g, np.roll(r, sh, axis=1)])

def fx_scanlines(frame, line_gap=4, darkness=50, **kw):
    result = frame.astype(np.float32)
    dark = 1.0 - float(darkness) * 0.01
    gap = max(1, int(line_gap))
    mask = np.ones(frame.shape[0], dtype=np.float32)
    mask[::gap] = dark
    result *= mask[:, np.newaxis, np.newaxis]
    return np.clip(result, 0, 255).astype(np.uint8)

def fx_quantize(frame, colors=8, **kw):
    n = max(2, int(colors))
    step = 256 // n
    return ((frame.astype(np.int32) // step) * step).clip(0, 255).astype(np.uint8)

def fx_vhs(frame, noise=8, track_error=3, frame_idx=0, **kw):
    result = fx_scanlines(frame, line_gap=2, darkness=20)
    result = fx_chromatic(result, shift=int(track_error))
    rng = np.random.default_rng(frame_idx)
    if float(noise) > 0:
        h, w = result.shape[:2]
        n = ((rng.random((h, w, 1)) - 0.5) * float(noise) * 3).astype(np.float32)
        result = np.clip(result.astype(np.float32) + n, 0, 255).astype(np.uint8)
    if rng.random() < 0.2:
        row = rng.integers(0, result.shape[0])
        result[row] = np.clip(result[row].astype(np.float32) * rng.uniform(0.7, 1.2), 0, 255).astype(np.uint8)
    return result

def fx_rgb_shift(frame, r_shift=8, g_shift=0, b_shift=-8, **kw):
    b, g, r = cv2.split(frame)
    return cv2.merge([
        np.roll(b, int(b_shift), axis=1),
        np.roll(g, int(g_shift), axis=0),
        np.roll(r, int(r_shift), axis=1),
    ])

def fx_mirror(frame, mode='horizontal', **kw):
    if mode == 'horizontal':
        half = frame[:, :frame.shape[1]//2]
        return np.concatenate([half, cv2.flip(half, 1)], axis=1)
    else:
        half = frame[:frame.shape[0]//2]
        return np.concatenate([half, cv2.flip(half, 0)], axis=0)

def fx_neon(frame, blur=3, boost=20, **kw):
    bl = max(1, int(blur))
    bl = bl if bl % 2 == 1 else bl + 1
    blurred = cv2.GaussianBlur(frame, (bl*4+1, bl*4+1), 0)
    edges = cv2.Canny(frame, 60, 150)
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    result = cv2.addWeighted(frame, 0.4, blurred, 0.2, 0)
    result = cv2.addWeighted(result, 1.0, edges_rgb, float(boost) * 0.1, 0)
    return np.clip(result, 0, 255).astype(np.uint8)


# ── Effect registry (param labels use translation keys) ───────────────────────

EFFECTS = {
    'pixelate': {
        'fn': fx_pixelate,
        'params': {
            'block_size': {'key': 'p_block_size', 'min': 2, 'max': 80, 'default': 16, 'step': 1},
        },
    },
    'wave': {
        'fn': fx_wave,
        'params': {
            'amplitude': {'key': 'p_amplitude', 'min': 1, 'max': 100, 'default': 20, 'step': 1},
            'frequency': {'key': 'p_frequency', 'min': 1, 'max': 100, 'default': 5,  'step': 1},
            'axis':      {'key': 'p_axis', 'type': 'choice',
                          'options': ['horizontal', 'vertical'], 'default': 'horizontal'},
        },
    },
    'stripes': {
        'fn': fx_stripes,
        'params': {
            'stripe_width': {'key': 'p_stripe_width', 'min': 1, 'max': 120, 'default': 10, 'step': 1},
            'opacity':      {'key': 'p_opacity',      'min': 0, 'max': 100, 'default': 60, 'step': 1},
            'orientation':  {'key': 'p_orientation', 'type': 'choice',
                             'options': ['horizontal', 'vertical'], 'default': 'horizontal'},
        },
    },
    'glitch': {
        'fn': fx_glitch,
        'params': {
            'intensity':    {'key': 'p_intensity',    'min': 1, 'max': 60,  'default': 8,  'step': 1},
            'block_height': {'key': 'p_block_height', 'min': 2, 'max': 100, 'default': 20, 'step': 1},
        },
    },
    'chromatic': {
        'fn': fx_chromatic,
        'params': {
            'shift': {'key': 'p_shift', 'min': 0, 'max': 60, 'default': 6, 'step': 1},
        },
    },
    'scanlines': {
        'fn': fx_scanlines,
        'params': {
            'line_gap': {'key': 'p_line_gap', 'min': 2, 'max': 30, 'default': 4,  'step': 1},
            'darkness': {'key': 'p_darkness', 'min': 0, 'max': 90, 'default': 50, 'step': 1},
        },
    },
    'quantize': {
        'fn': fx_quantize,
        'params': {
            'colors': {'key': 'p_colors', 'min': 2, 'max': 64, 'default': 8, 'step': 1},
        },
    },
    'vhs': {
        'fn': fx_vhs,
        'params': {
            'noise':       {'key': 'p_noise',       'min': 0, 'max': 60, 'default': 8, 'step': 1},
            'track_error': {'key': 'p_track_error', 'min': 0, 'max': 20, 'default': 3, 'step': 1},
        },
    },
    'rgb_shift': {
        'fn': fx_rgb_shift,
        'params': {
            'r_shift': {'key': 'p_r_shift', 'min': -40, 'max': 40, 'default': 8,  'step': 1},
            'g_shift': {'key': 'p_g_shift', 'min': -40, 'max': 40, 'default': 0,  'step': 1},
            'b_shift': {'key': 'p_b_shift', 'min': -40, 'max': 40, 'default': -8, 'step': 1},
        },
    },
    'mirror': {
        'fn': fx_mirror,
        'params': {
            'mode': {'key': 'p_mode', 'type': 'choice',
                     'options': ['horizontal', 'vertical'], 'default': 'horizontal'},
        },
    },
    'neon': {
        'fn': fx_neon,
        'params': {
            'blur':  {'key': 'p_blur',  'min': 1, 'max': 10, 'default': 3,  'step': 1},
            'boost': {'key': 'p_boost', 'min': 1, 'max': 50, 'default': 20, 'step': 1},
        },
    },
}

EFFECT_KEYS = list(EFFECTS.keys())


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def fmt_time(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def fmt_size(nbytes):
    if nbytes < 1024:        return f"{nbytes} B"
    elif nbytes < 1024**2:   return f"{nbytes/1024:.1f} KB"
    elif nbytes < 1024**3:   return f"{nbytes/1024**2:.2f} MB"
    return f"{nbytes/1024**3:.2f} GB"


# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class VideoVisualEffectsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VideoVisualEffects")
        self.root.geometry("680x560")
        self.root.minsize(580, 500)
        self.root.resizable(False, False)

        self.current_lang = 'ru'
        self.active_tab   = 'process'
        self.is_running   = False
        self._start_time  = None
        self._timer_id    = None
        self._cur_frame   = 0
        self._tot_frames  = 0
        self._stop_event  = threading.Event()

        # Vars
        self.in_var         = tk.StringVar()
        self.out_var        = tk.StringVar()
        self.effect_key_var = tk.StringVar(value='pixelate')
        self.effect_lbl_var = tk.StringVar()
        self.progress_var   = tk.DoubleVar(value=0.0)
        self.elapsed_var    = tk.StringVar(value="--:--")
        self.remaining_var  = tk.StringVar(value="--:--")
        self.frame_var      = tk.StringVar(value="—")
        self.src_fps_var    = tk.StringVar(value="—")
        self.res_var        = tk.StringVar(value="—")
        self.size_var       = tk.StringVar(value="—")
        self.status_var     = tk.StringVar(value="")
        self.desc_var       = tk.StringVar(value="")
        self.lang_var       = tk.StringVar(value=LANGUAGE_NAMES['ru'])

        # Settings
        self.out_fps_var   = tk.IntVar(value=0)
        self.res_scale_var = tk.IntVar(value=100)
        self.codec_var     = tk.StringVar(value='mp4v')

        # Per-effect param vars / frames / label widgets
        self._param_vars    = {}
        self._param_frames  = {}
        self._param_lbl_wgts = {}   # {key: {pname: tk.Label}}

        self.display_to_code = {LANGUAGE_NAMES[c]: c for c in LANG_ORDER}

        self._load_icon()
        self._build_ui()
        self._apply_language()
        self._show_tab('process')
        self._select_effect('pixelate')

        self.root.mainloop()

    # ── icon ──────────────────────────────────────────────────────────────────

    def _load_icon(self):
        try:
            base = os.path.dirname(os.path.abspath(__file__))
            ico  = os.path.join(base, 'DATA', 'ico.ico')
            if os.path.exists(ico):
                self.root.iconbitmap(ico)
        except Exception:
            pass

    def t(self, key):
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS['en']).get(
            key, TRANSLATIONS['en'].get(key, key))

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Tab bar
        tab_bar = tk.Frame(self.root, relief='flat', bd=0)
        tab_bar.grid(row=0, column=0, sticky='ew', padx=2, pady=(4, 0))
        self._tab_btns = {}
        for name in ('process', 'settings'):
            b = tk.Button(tab_bar, command=lambda n=name: self._show_tab(n))
            b.pack(side='left', padx=2, pady=2)
            self._tab_btns[name] = b

        # Content host
        self.content_host = tk.Frame(self.root)
        self.content_host.grid(row=1, column=0, sticky='nsew', padx=4, pady=4)
        self.content_host.columnconfigure(0, weight=1)
        self.content_host.rowconfigure(0, weight=1)

        self._tabs = {
            'process':  self._build_process_tab(),
            'settings': self._build_settings_tab(),
        }
        for frm in self._tabs.values():
            frm.place(in_=self.content_host, relwidth=1, relheight=1)

        # Footer
        self.footer = tk.Frame(self.root, relief='sunken', bd=1)
        self.footer.grid(row=2, column=0, sticky='ew')
        tk.Label(self.footer, text='VideoVisualEffects v1.1  |  Python · OpenCV · NumPy',
                 font=('TkDefaultFont', 7)).pack(side='left', padx=6, pady=2)

    # ── Process tab ───────────────────────────────────────────────────────────

    def _build_process_tab(self):
        f = tk.Frame(self.content_host)
        f.columnconfigure(1, weight=1)

        # Input
        self._lbl_input = tk.Label(f)
        self._lbl_input.grid(row=0, column=0, sticky='w', padx=(8, 4), pady=(10, 3))
        tk.Entry(f, textvariable=self.in_var).grid(row=0, column=1, sticky='ew', pady=(10, 3))
        self._btn_in = tk.Button(f, command=self._browse_in)
        self._btn_in.grid(row=0, column=2, padx=(4, 8), pady=(10, 3))

        # Output
        self._lbl_output = tk.Label(f)
        self._lbl_output.grid(row=1, column=0, sticky='w', padx=(8, 4), pady=3)
        tk.Entry(f, textvariable=self.out_var).grid(row=1, column=1, sticky='ew', pady=3)
        self._btn_out = tk.Button(f, command=self._browse_out)
        self._btn_out.grid(row=1, column=2, padx=(4, 8), pady=3)

        # Effect selector row
        self._lbl_effect = tk.Label(f)
        self._lbl_effect.grid(row=2, column=0, sticky='w', padx=(8, 4), pady=3)
        combo_frame = tk.Frame(f)
        combo_frame.grid(row=2, column=1, columnspan=2, sticky='ew', pady=3, padx=(0, 8))
        combo_frame.columnconfigure(0, weight=0)
        combo_frame.columnconfigure(1, weight=1)
        self._eff_combo = ttk.Combobox(combo_frame, textvariable=self.effect_lbl_var,
                                       state='readonly', width=26)
        self._eff_combo.grid(row=0, column=0, sticky='w', padx=(0, 8))
        self._eff_combo.bind('<<ComboboxSelected>>', self._on_effect_combo)
        # Description label (italic, small)
        self._desc_lbl = tk.Label(combo_frame, textvariable=self.desc_var,
                                  font=('TkDefaultFont', 7, 'italic'),
                                  fg='#555555', anchor='w', justify='left', wraplength=320)
        self._desc_lbl.grid(row=0, column=1, sticky='ew')

        # Start / Stop / Status
        ctrl = tk.Frame(f)
        ctrl.grid(row=3, column=0, columnspan=3, sticky='w', padx=8, pady=(8, 2))
        self.start_btn = tk.Button(ctrl, command=self._start_process)
        self.start_btn.pack(side='left', padx=(0, 6))
        self.stop_btn = tk.Button(ctrl, command=self._stop_process, state='disabled')
        self.stop_btn.pack(side='left', padx=(0, 10))
        self._lbl_status_key = tk.Label(ctrl, font=('TkDefaultFont', 8))
        self._lbl_status_key.pack(side='left')
        tk.Label(ctrl, textvariable=self.status_var,
                 font=('TkDefaultFont', 8)).pack(side='left')

        # Progress
        self.progress = ttk.Progressbar(f, variable=self.progress_var,
                                        maximum=100, mode='determinate', length=300)
        self.progress.grid(row=4, column=0, columnspan=3,
                           sticky='ew', padx=8, pady=(2, 4))

        # Params LabelFrame
        self._params_lf = tk.LabelFrame(f, padx=6, pady=4)
        self._params_lf.grid(row=5, column=0, columnspan=3,
                              sticky='ew', padx=8, pady=(0, 4))
        self._params_lf.columnconfigure(0, weight=1)
        self._params_host = tk.Frame(self._params_lf)
        self._params_host.grid(row=0, column=0, sticky='ew')
        self._params_host.columnconfigure(1, weight=1)

        # Build hidden param frames per effect
        for key, eff in EFFECTS.items():
            pf = tk.Frame(self._params_host)
            pf.columnconfigure(1, weight=1)
            self._param_frames[key] = pf
            self._param_vars[key]   = {}
            self._param_lbl_wgts[key] = {}
            for ridx, (pname, pdef) in enumerate(eff['params'].items()):
                ptype = pdef.get('type', 'slider')
                lbl = tk.Label(pf, font=('TkDefaultFont', 8))
                lbl.grid(row=ridx, column=0, sticky='w', padx=(0, 10), pady=1)
                self._param_lbl_wgts[key][pname] = lbl
                if ptype == 'slider':
                    var = tk.IntVar(value=int(pdef['default']))
                    val_lbl = tk.Label(pf, text=str(pdef['default']),
                                       font=('TkDefaultFont', 8), width=5, anchor='e')
                    val_lbl.grid(row=ridx, column=2, sticky='e', padx=(4, 0), pady=1)
                    tk.Scale(pf, from_=pdef['min'], to=pdef['max'],
                             variable=var, orient='horizontal', showvalue=False,
                             length=240, resolution=pdef.get('step', 1),
                             command=lambda v, vl=val_lbl: vl.config(text=str(int(float(v))))).grid(
                        row=ridx, column=1, sticky='ew', pady=1)
                    self._param_vars[key][pname] = var
                elif ptype == 'choice':
                    var = tk.StringVar(value=pdef['default'])
                    tk.OptionMenu(pf, var, *pdef['options']).grid(
                        row=ridx, column=1, sticky='w', pady=1)
                    self._param_vars[key][pname] = var

        # Stats LabelFrame
        self._info_lf = tk.LabelFrame(f, padx=6, pady=4)
        self._info_lf.grid(row=6, column=0, columnspan=3,
                           sticky='ew', padx=8, pady=(0, 8))
        self._info_lf.columnconfigure(1, weight=1)
        self._info_lf.columnconfigure(3, weight=1)

        def _slbl(parent, r, c, tvar):
            lbl = tk.Label(parent, anchor='e', font=('TkDefaultFont', 8, 'bold'))
            lbl.grid(row=r, column=c, sticky='e', padx=(4, 2))
            tk.Label(parent, textvariable=tvar, anchor='w',
                     font=('TkDefaultFont', 8)).grid(row=r, column=c+1, sticky='w', padx=(0, 10))
            return lbl

        self._lbl_elapsed   = _slbl(self._info_lf, 0, 0, self.elapsed_var)
        self._lbl_remaining = _slbl(self._info_lf, 0, 2, self.remaining_var)
        self._lbl_frame     = _slbl(self._info_lf, 1, 0, self.frame_var)
        self._lbl_fps       = _slbl(self._info_lf, 1, 2, self.src_fps_var)
        self._lbl_res       = _slbl(self._info_lf, 2, 0, self.res_var)
        self._lbl_size      = _slbl(self._info_lf, 2, 2, self.size_var)

        return f

    # ── Settings tab ──────────────────────────────────────────────────────────

    def _build_settings_tab(self):
        f = tk.Frame(self.content_host)
        f.columnconfigure(1, weight=1)

        # Language
        self._lbl_lang = tk.Label(f)
        self._lbl_lang.grid(row=0, column=0, sticky='w', padx=(8, 4), pady=(10, 4))
        lang_names = [LANGUAGE_NAMES[c] for c in LANG_ORDER]
        self.lang_menu = tk.OptionMenu(f, self.lang_var, *lang_names,
                                       command=self._on_lang_change)
        self.lang_menu.grid(row=0, column=1, sticky='w', pady=(10, 4))

        # FPS
        self._lbl_fps_s = tk.Label(f)
        self._lbl_fps_s.grid(row=1, column=0, sticky='w', padx=(8, 4), pady=3)
        fps_row = tk.Frame(f)
        fps_row.grid(row=1, column=1, sticky='w', pady=3)
        self._fps_val_lbl = tk.Label(fps_row, font=('TkDefaultFont', 8), width=12)
        self._fps_val_lbl.pack(side='right')
        tk.Scale(fps_row, from_=0, to=60, variable=self.out_fps_var,
                 orient='horizontal', showvalue=False, length=200,
                 command=self._on_fps_change).pack(side='left')

        # Scale
        self._lbl_scale = tk.Label(f)
        self._lbl_scale.grid(row=2, column=0, sticky='w', padx=(8, 4), pady=3)
        res_row = tk.Frame(f)
        res_row.grid(row=2, column=1, sticky='w', pady=3)
        self._scale_val_lbl = tk.Label(res_row, text='100 %',
                                       font=('TkDefaultFont', 8), width=12)
        self._scale_val_lbl.pack(side='right')
        tk.Scale(res_row, from_=25, to=200, variable=self.res_scale_var,
                 orient='horizontal', showvalue=False, length=200, resolution=5,
                 command=lambda v: self._scale_val_lbl.config(
                     text=f'{int(float(v))} %')).pack(side='left')

        # Codec
        self._lbl_codec = tk.Label(f)
        self._lbl_codec.grid(row=3, column=0, sticky='w', padx=(8, 4), pady=3)
        codec_row = tk.Frame(f)
        codec_row.grid(row=3, column=1, sticky='w', pady=3)
        for codec in ['mp4v', 'avc1', 'XVID', 'MJPG']:
            tk.Radiobutton(codec_row, text=codec, variable=self.codec_var,
                           value=codec).pack(side='left', padx=(0, 10))

        # Hints
        self._hints_lf = tk.LabelFrame(f, padx=8, pady=6)
        self._hints_lf.grid(row=4, column=0, columnspan=3, sticky='ew',
                            padx=8, pady=(12, 0))
        self._hints_text = tk.Label(self._hints_lf, justify='left',
                                    font=('TkDefaultFont', 8))
        self._hints_text.pack(anchor='w')

        return f

    # ── Tabs ──────────────────────────────────────────────────────────────────

    def _show_tab(self, name):
        self.active_tab = name
        for n, frm in self._tabs.items():
            frm.lift() if n == name else frm.lower()
        for n, b in self._tab_btns.items():
            b.config(relief='sunken' if n == name else 'raised')

    # ── Effect selection ──────────────────────────────────────────────────────

    def _on_effect_combo(self, _event=None):
        label = self.effect_lbl_var.get()
        key = next((k for k in EFFECT_KEYS
                    if self.t(f'fx_{k}') == label), EFFECT_KEYS[0])
        self._select_effect(key)

    def _select_effect(self, key):
        self.effect_key_var.set(key)
        self.effect_lbl_var.set(self.t(f'fx_{key}'))
        self.desc_var.set(self.t(f'desc_{key}'))
        for k, pf in self._param_frames.items():
            if k == key:
                pf.grid(row=0, column=0, sticky='ew')
            else:
                pf.grid_remove()

    # ── Language ──────────────────────────────────────────────────────────────

    def _on_lang_change(self, display_name):
        self.current_lang = self.display_to_code.get(display_name, 'en')
        self._apply_language()

    def _on_fps_change(self, v):
        auto = self.t('out_fps_auto')
        iv = int(float(v))
        self._fps_val_lbl.config(text=f'{iv} FPS' if iv > 0 else auto)

    def _apply_language(self):
        # Tabs
        for name, btn in self._tab_btns.items():
            btn.config(text=self.t(name))

        # Process tab labels
        self._lbl_input.config(text=self.t('input_file'))
        self._lbl_output.config(text=self.t('output_file'))
        self._lbl_effect.config(text=self.t('effect'))
        self._btn_in.config(text=self.t('browse'))
        self._btn_out.config(text=self.t('browse'))
        self.start_btn.config(text=self.t('start'))
        self.stop_btn.config(text=self.t('stop'))
        self._lbl_status_key.config(text=self.t('status') + ' ')
        self.status_var.set(self.t('ready'))

        # Params labelframe
        self._params_lf.config(text=self.t('params_lf'))

        # Param labels inside each effect frame
        for key, eff in EFFECTS.items():
            for pname, pdef in eff['params'].items():
                lbl_wgt = self._param_lbl_wgts[key].get(pname)
                if lbl_wgt:
                    lbl_wgt.config(text=self.t(pdef['key']))

        # Stats labelframe + stat labels
        self._info_lf.config(text=self.t('info_lf'))
        self._lbl_elapsed.config(text=self.t('stat_elapsed'))
        self._lbl_remaining.config(text=self.t('stat_remaining'))
        self._lbl_frame.config(text=self.t('stat_frame'))
        self._lbl_fps.config(text=self.t('stat_fps'))
        self._lbl_res.config(text=self.t('stat_res'))
        self._lbl_size.config(text=self.t('stat_size'))

        # Settings tab
        self._lbl_lang.config(text=self.t('language'))
        self._lbl_fps_s.config(text=self.t('out_fps'))
        self._lbl_scale.config(text=self.t('scale'))
        self._lbl_codec.config(text=self.t('codec'))
        self._hints_lf.config(text=self.t('hints_lf'))
        self._hints_text.config(text=self.t('hints'))
        self._on_fps_change(self.out_fps_var.get())

        # Refresh effect combobox values in current language
        new_names = [self.t(f'fx_{k}') for k in EFFECT_KEYS]
        self._eff_combo.config(values=new_names)

        # Re-select current effect (updates label + description)
        self._select_effect(self.effect_key_var.get())

        # Refresh tab buttons
        for n, b in self._tab_btns.items():
            b.config(relief='sunken' if n == self.active_tab else 'raised')

    # ── Browse ────────────────────────────────────────────────────────────────

    def _browse_in(self):
        p = filedialog.askopenfilename(
            title=self.t('select_input'),
            filetypes=[(self.t('video_files'),
                        '*.mp4 *.avi *.mkv *.mov *.webm *.flv'),
                       (self.t('all_files'), '*.*')])
        if not p:
            return
        self.in_var.set(p)
        try:
            self.size_var.set(fmt_size(os.path.getsize(p)))
            cap = cv2.VideoCapture(p)
            self.res_var.set(f'{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}×'
                             f'{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}')
            self.src_fps_var.set(f'{cap.get(cv2.CAP_PROP_FPS):.1f}')
            cap.release()
        except Exception:
            pass
        if not self.out_var.get():
            base, _ = os.path.splitext(p)
            self.out_var.set(base + '_fx.mp4')

    def _browse_out(self):
        p = filedialog.asksaveasfilename(
            title=self.t('select_output'), defaultextension='.mp4',
            filetypes=[('MP4', '*.mp4'), ('AVI', '*.avi'),
                       (self.t('all_files'), '*.*')])
        if p:
            self.out_var.set(p)

    # ── Timer ─────────────────────────────────────────────────────────────────

    def _tick(self):
        if not self.is_running:
            return
        elapsed = time.time() - self._start_time
        self.elapsed_var.set(fmt_time(elapsed))
        if self._tot_frames > 0 and self._cur_frame > 0:
            rate = self._cur_frame / elapsed
            self.remaining_var.set('~' + fmt_time(
                (self._tot_frames - self._cur_frame) / rate))
        self._timer_id = self.root.after(500, self._tick)

    def _stop_timer(self):
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None

    # ── Process ───────────────────────────────────────────────────────────────

    def _start_process(self):
        if self.is_running:
            return
        if not BACKEND_AVAILABLE:
            messagebox.showerror('VideoVisualEffects', f'OpenCV: {_BACKEND_ERROR}')
            return
        inp = self.in_var.get().strip()
        out = self.out_var.get().strip()
        if not inp:
            messagebox.showwarning('VideoVisualEffects', self.t('warn_no_input'))
            return
        if not out:
            messagebox.showwarning('VideoVisualEffects', self.t('warn_no_output'))
            return

        key    = self.effect_key_var.get()
        params = {pn: var.get() for pn, var in self._param_vars[key].items()}
        fps    = self.out_fps_var.get()
        scale  = self.res_scale_var.get() / 100.0
        codec  = self.codec_var.get()

        self.is_running = True
        self._stop_event.clear()
        self._start_time = time.time()
        self._cur_frame  = 0
        self._tot_frames = 0
        self.progress_var.set(0.0)
        self.elapsed_var.set('00:00')
        self.remaining_var.set('--:--')
        self.frame_var.set('—')
        self.status_var.set(self.t('processing'))
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self._timer_id = self.root.after(500, self._tick)

        threading.Thread(
            target=self._run_process,
            args=(inp, out, key, params, fps, scale, codec),
            daemon=True,
        ).start()

    def _stop_process(self):
        self._stop_event.set()

    def _run_process(self, inp, out, effect_key, params, out_fps, res_scale, codec):
        ok = False
        frames_done = 0
        err_msg = ''
        try:
            cap   = cv2.VideoCapture(inp)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            s_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            s_w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            s_h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            d_fps = float(out_fps) if out_fps > 0 else s_fps
            d_w   = max(2, int(s_w * res_scale) // 2 * 2)
            d_h   = max(2, int(s_h * res_scale) // 2 * 2)
            writer = cv2.VideoWriter(out, cv2.VideoWriter_fourcc(*codec), d_fps, (d_w, d_h))
            fx_fn = EFFECTS[effect_key]['fn']
            fn = 0
            while True:
                if self._stop_event.is_set():
                    break
                ret, frame = cap.read()
                if not ret:
                    break
                if res_scale != 1.0:
                    frame = cv2.resize(frame, (d_w, d_h), interpolation=cv2.INTER_AREA)
                writer.write(fx_fn(frame, frame_idx=fn, **params))
                fn += 1
                frames_done = fn
                if fn % 4 == 0 or fn == total:
                    pct = fn / total * 100.0 if total > 0 else 0.0
                    self._cur_frame  = fn
                    self._tot_frames = total
                    self.root.after(0, lambda p=pct, c=fn, t=total: (
                        self.progress_var.set(p),
                        self.frame_var.set(f'{c} / {t}'),
                    ))
            cap.release()
            writer.release()
            ok = not self._stop_event.is_set()
        except Exception as e:
            ok = False
            err_msg = str(e)

        elapsed = time.time() - self._start_time

        def _finish():
            self._stop_timer()
            self.is_running = False
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self._load_icon()
            if ok:
                self.progress_var.set(100.0)
                self.status_var.set(self.t('done'))
                try:   sz = fmt_size(os.path.getsize(out))
                except: sz = '—'
                messagebox.showinfo(
                    self.t('done_title'),
                    self.t('done_msg').format(
                        t=fmt_time(elapsed),
                        eff=self.t(f'fx_{effect_key}'),
                        out=out, sz=sz, fr=frames_done))
            elif self._stop_event.is_set():
                self.status_var.set(self.t('stopped'))
            else:
                self.status_var.set(self.t('error'))
                messagebox.showerror(
                    self.t('err_title'),
                    self.t('err_msg').format(t=fmt_time(elapsed), e=err_msg))

        self.root.after(0, _finish)


# ─────────────────────────────────────────────────────────────────────────────

def main():
    VideoVisualEffectsApp()

if __name__ == '__main__':
    main()
