Features:
    - Maybe something to interface with yomitan
    - Built in clipboard inserter?
    - Built in hooker? (textractor plugin?)
    - Automatic script for fixing forvo and google images
    - UI is kinda shit tbh
        - Please improve the UI to be more user friendly, and easily customizible.
        - User themes and settings should be managed well, and creating them should be more seemless and effortless (right now its clunky)



- Please can you check the code base and look for other things to make the codebase fully refactored. After phase 4 I don't think our refactor is 100% complete.

- shouldnt all of the like bs4 and stuff cluttering the root directory be in a libs dir or something? Please organize the project directory better while ensuring that it can still be read as an anki addon correctly. Have a directory for legacy code etc. Where things are still being used post refactor, please can you neaten them up too?


- According to the task 12 final report theres still a bunch of errors and missing coverage. Please fix this.

- right now the user files are not being properly generated etc... Would be nice if they transfer with anki web account... user_files should all be in gitignore
