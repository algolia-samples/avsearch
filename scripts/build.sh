#!/bin/bash
if ! ./scripts/pre-commit.sh; then
    echo "Please correct the issues above before attempting to build."
    exit 1
fi

# Run the poetry build process
poetry build

if [ $? -ne 0 ]; then
    echo "An issue occurred during the build process - double check the output above and try again."
    exit 1
else
    echo "The build finished successfully!"
fi
