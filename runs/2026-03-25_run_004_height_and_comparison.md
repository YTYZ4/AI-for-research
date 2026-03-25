# run 004 - height shrink and comparison experiments

date: 2026-03-25
stage: add height shrink and generate report comparison assets

## what was implemented
- add height shrinking via transpose-reuse of vertical seam logic
- keep seam carving in shrink-only mode (no enlarging in this stage)
- clamp GUI targets to avoid accidental enlarge requests

## test images
- subject-focused: bing1.png
- landscape-rich: original.png

## generated outputs
for each case folder under outputs/hw1_op1:
- original.png
- resize_linear.png
- crop.png
- seam_width.png
- seam_height.png
- compare_grid.png

## runtime summary
- bing1.png seam_width: 17.9682 s
- bing1.png seam_height: 5.0191 s
- original.png seam_width: 33.6628 s
- original.png seam_height: 16.9417 s

## notes
- to keep runtime stable in pure Python loop, inputs are downscaled to max_side=420 before carving
- metrics table updated with unified schema requested in step 6
