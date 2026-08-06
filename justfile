# List availale recipes
default:
    @just --list

# Run all code quality checks (formatting, clippy and tests)
check: fmt clippy test

# Format the codebase using rustfmt
fmt:
    cargo fmt --all -- --check

# Run clippy with strict warnings enabled on all targets (including tests)
clippy:
    cargo clippy --workspace --all-targets -- -D warnings

# Build the crate
build:
    uv run maturin build --features zenoh --release

# Execute the test suite
test:
    uv run pytest

# Clean build artifacts
clean:
    cargo clean
