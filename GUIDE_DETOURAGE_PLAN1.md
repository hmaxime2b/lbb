# Guide Détourage Plan 1 — LBB (Maillot Blanc, Nuit)

## Analyse de l'image

**Avantages pour le détourage :**
- Maillot blanc très clair sur fond de stade sombre → fort contraste
- Casque blanc = contour net
- Éclairage stade crée une séparation naturelle joueur/fond

**Difficultés :**
- Deuxième joueur derrière (à exclure du masque)
- Bras partiellement devant le panneau LED
- Jeu de jambes potentiellement flou

---

## Méthode Premiere Pro (rapide, ~20min)

### Étape 1 — Dupliquer le clip
1. `Alt + clic` sur le clip V1 → faire glisser sur V2
2. Le clip dupliqué est sur la piste du dessus

### Étape 2 — Masque libre (Pen tool)
1. Sélectionner le clip sur V2
2. `Effets de maîtrise` → `Opacité`
3. Cliquer l'icône **stylo** (Pen tool)
4. Tracer le contour de LBB :
   - Commencer par la tête (casque blanc)
   - Suivre l'épaule droite → bras → main
   - Descendre le long du corps
   - Contourner les jambes
   - Remonter côté gauche
5. **Feather** : régler à **8-12px** (adoucit les bords)

### Étape 3 — Exclure le joueur derrière
1. Dans le même panel Opacité, cliquer **"Ajouter un masque"**
2. Tracer le contour du 2ème joueur
3. Cocher **"Inverser"** sur CE masque uniquement
→ Le masque de soustraction efface le joueur du fond

### Étape 4 — Tracking du masque (si clip en mouvement)
1. Dans les propriétés du masque → icône **"Tracker"**
2. Cliquer **"Track Selected Forward"** ▶
3. Premiere suit automatiquement le masque frame par frame
4. Corriger manuellement les frames où le tracking déraille

### Étape 5 — Remplacement du fond
**Option A — Fond noir simple :**
- Créer un clip couleur noire sous V1
- Le masque sur V2 montre LBB, le fond noir apparaît dessous

**Option B — Fond stylisé (gradient sombre) :**
- `Nouveau` → `Dégradé` → sombre du bas vers le haut
- Cela simule l'ambiance stade nuit

---

## Méthode Blender Masque (propre, ~45min)

```
Movie Clip Editor → Onglet "Mask"
→ New Mask
→ Tracer avec points Bezier (G pour déplacer, E pour extruder)
→ Motion Tracking : tracker sur épaule, casque, hanche
→ Parent chaque point masque au tracker correspondant
→ Render → Output RGBA (PNG séquence)
```

---

## Checklist avant le freeze frame

- [ ] LBB visible, fond supprimé ou remplacé
- [ ] Bords nets (Feather 8-12px)
- [ ] 2ème joueur exclu
- [ ] Panneau "BIELLE-BIARREY" visible ou masqué selon choix artistique
- [ ] Test : lire le clip, vérifier que le masque suit le mouvement

---

## Note artistique — Plan 2 (Klaxon)

Le plan klaxon (maillot bleu, bras levé) est en plein jour.
**Ne pas détourageer ce plan** — garder le contexte stade + foule
qui applaudit → ça renforce l'impact émotionnel de la célébration.
