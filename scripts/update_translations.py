"""Update README translations using PO files in locale."""

import os

from mdpo import markdown_to_pofile, pofile_to_markdown


LANGUAGES = (
    'es',
)


def main():
    exitcode = 0

    if not os.path.isdir('locale'):
        os.mkdir('locale')

    for language in LANGUAGES:
        language_dir = os.path.join('locale', language)
        if not os.path.isdir(language_dir):
            os.mkdir(language_dir)

        po_filepath = os.path.join(language_dir, 'README.po')
        po = markdown_to_pofile(
            'README.md', location=False, po_filepath=po_filepath,
        )
        po.save(po_filepath)

        readme_filepath = os.path.join(language_dir, 'README.md')
        pofile_to_markdown(
            'README.md', po_filepath, save=readme_filepath, wrapwidth=999,
        )

    return exitcode


if __name__ == '__main__':
    main()
