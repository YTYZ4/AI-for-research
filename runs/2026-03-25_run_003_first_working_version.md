# run 003 - first working version (width only)

date: 2026-03-25
stage: first minimal closed loop for seam carving width shrink

## goal
- remove 1 seam successfully
- remove 10 seams successfully
- remove seams until target width successfully

## code location
- solutions/hw1_op1/reference_template/seam_carving.py
- solutions/hw1_op1/src/run_first_working_width_only.py

## first successful run summary
- input image: outputs based on solutions/hw1_op1/figs/original.png
- input size: (339, 510, 3)
- output sizes:
  - remove_1_seam.png: (339, 509, 3)
  - remove_10_seams.png: (339, 500, 3)
  - remove_to_target_width.png: (339, 306, 3)
- required debug outputs generated:
  - energy_map.png
  - seam_overlay.png
  - remove_1_seam.png
  - remove_10_seams.png

## error status
- runtime crash in seam carving core: no
- temporary execution issue in launcher: yes
  - issue: `conda run -n mm26 ...` returned `CondaError: KeyboardInterrupt` in this terminal session
  - fix: use direct interpreter path `C:\Users\ydyz0\.conda\envs\mm26\python.exe ...`
  - result: run succeeded and outputs were generated

## debug rounds
- round 1: implement compute energy + dp + backtrack + remove seam + loop
- round 2: add output exporter and run, command wrapper failed (KeyboardInterrupt)
- round 3: switch to direct mm26 python executable, run passed
- total rounds: 3

## focused checks (only 4 common mistakes)
- dp boundary out-of-bounds: checked by left/right clamp and successful run
- non-continuous seam from backtracking: checked with assertion `abs(diff(seam)) <= 1`
- invalid image shape after removal: checked with assertion `width decreases by 1`
- forgot to recompute energy after each seam: fixed by recomputing in every loop iteration

## current conclusion
- width-only seam carving minimal version is working
- program does not crash on the tested image
- image width is clearly reduced
