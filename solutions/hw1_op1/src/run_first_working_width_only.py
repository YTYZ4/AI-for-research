from pathlib import Path
import sys

def main():
    repo_root = Path(__file__).resolve().parents[3]
    ref_dir = repo_root / 'solutions' / 'hw1_op1' / 'reference_template'
    sys.path.insert(0, str(ref_dir))

    from seam_carving import export_first_working_outputs

    input_image = repo_root / 'solutions' / 'hw1_op1' / 'figs' / 'original.png'
    output_dir = repo_root / 'outputs' / 'hw1_op1'
    export_first_working_outputs(input_image, output_dir)
    print(f'Exported debug outputs to: {output_dir}')


if __name__ == '__main__':
    main()
