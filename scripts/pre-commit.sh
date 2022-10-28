# Ensure we are within a poetry shell
if [ -z $POETRY_ACTIVE ]; then
    echo "Poetry shell not active, attempting to start..."
    poetry shell
fi

# Black
echo "---- Black ----"
black \
    --line-length=120 \
    --target-version=py37 \
    avsearch

if [ $? -ne 0 ]; then
    echo "An issue was observed with Black - double check the output and re-run if needed."
    exit 1
fi

# Flake8
echo "---- Flake8 ----"
flake8 \
    --max-line-length=120 \
    --per-file-ignores=avsearch/__init__.py:F401 \
    avsearch

if [ $? -ne 0 ]; then
    echo "An issue was observed with Flake8 - double check the output and re-run if needed."
    exit 1
fi

echo "All done!";