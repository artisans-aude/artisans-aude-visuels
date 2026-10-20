# Gabarit des réels Artisans Aude (validé par Grégory le 17/10/2026)

- Format : MP4 vertical 1080×1920, 25 i/s, environ 42 s, style « Dégradé solaire ».
- Rythme de lecture : chaque écran reste 6 à 8 s ; éléments qui apparaissent un par un (0,6 s d'écart).
- Contenu : accroche → 4 chiffres clés (un par écran, carte blanche) → question finale sur fond prune + source.
- Zone utile : texte entre 400 px du haut et ~1 500 px (le bas est couvert par l'interface Reels). Aucun nom, aucune photo.
- Musique (choix de Grégory du 20/10/2026, remplace music.py et music_reflexion.py) : extrait de 42 s, uniquement les phases calmes (sans grosse caisse ni drop) de « Weekend » de Jarico feat. Vlad Gluschenko (Cervonext Electro Music, morceau présenté comme libre de droits), coupé sur les mesures (104 BPM), fondu de fin, niveau moyen ≈ −19 dB. Fichier prêt : outils/reel/musique_reels.mp3 (à utiliser tel quel pour chaque réel de 42 s). Montage : montage_musique_weekend.py (source MP3 non versionnée). CRÉDIT À AJOUTER à la fin de chaque texte de réel : « 🎵 Musique : Jarico feat. Vlad Gluschenko – Weekend (Cervonext Electro Music) ». Risque : Meta peut détecter le morceau (son coupé ou réel bloqué) ; si cela arrive, revenir à music_reflexion.py.
- Changements d'écran calés sur les mesures (multiples de 2 s).

Fabrication :
1. Copier reel.html, adapter les 6 sections et le tableau S (débuts/fins), et D (durée).
2. python3 render.py reel.html frames 42
3. Musique : utiliser outils/reel/musique_reels.mp3 (42 s) ; secours : python3 music_reflexion.py 42 → musique.wav
4. ffmpeg -framerate 25 -i frames/f%04d.jpg -i musique_reels.mp3 -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a aac -b:a 192k -shortest -movflags +faststart AAAA-MM-JJ_Reel_Sujet.mp4
5. Couverture : une image de l'écran d'accroche en JPG.
