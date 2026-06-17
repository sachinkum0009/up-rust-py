This repository provides Python bindings for the [Eclipse uProtocol Rust](https://github.com/eclipse-uprotocol/up-rust) library. Built using PyO3, it allows developers to seamlessly integrate high-performance, low-overhead uProtocol communication into their Python applications.

---

## Features

- 🚀 **High Performance**: Rust-powered implementations with minimal Python overhead
- 🔒 **Type Safe**: Full type hints and stub files for excellent IDE support
- 📡 **Complete uProtocol Support**: Publishers, Notifiers, and Transport implementations
- 🐍 **Pythonic API**: Easy-to-use interfaces that feel natural in Python
- ⚡ **Async Ready**: Built on Tokio async runtime for efficient I/O operations

## Build & Install

To build the `up-rust-py`, you need to install **uv** (python project manager) and **rust toolchain**. Follow this [link](https://docs.astral.sh/uv/getting-started/installation/) to install uv and this [link](https://rust-lang.org/tools/install/) to install rust toolchain.

**Build from source using uv**

```bash
# Clone the repository
git clone https://github.com/eclipse-uprotocol/up-rust-py.git
cd up-rust-py
uv sync

uv run maturin build
# To build with zenoh
uv run maturin build --features zenoh
```

## Quick Start

Before running the below examples, you need to follow above commands to *build from source using uv*.

### Simple Publisher (Local Transport)

For in-process communication without network overhead:

```bash
uv run examples/simple_publish.py

uv run examples/simple_notify.py
```

## Zenoh Publisher and Subscriber

For zenoh communication

```bash
uv run examples/simple_zenoh_publisher.py

uv run examples/simple_zenoh_subscriber.py
```

## Development

To build `up-rust-py` in development mode, you need to run the following commands.  

```bash
# Clone the repository
git clone https://github.com/eclipse-uprotocol/up-rust-py.git
cd up-rust-py

# Build in development mode
uv run maturin develop --features all

# Run tests
uv run pytest
```

### Building Wheels

```bash
# Build release wheel
uv run maturin build --release

# Build and publish to PyPI
uv run maturin publish
```

## Architecture

up-rust-py bridges Python and Rust using [PyO3](https://pyo3.rs/):

- **Rust Core**: High-performance implementations from [up-rust](https://github.com/eclipse-uprotocol/up-rust)
- **PyO3 Bindings**: Zero-cost abstractions between Python and Rust
- **Python API**: Pythonic interfaces with full type hints

Each async operation maintains its own Tokio runtime for thread-safe execution across the Python/Rust boundary.

## Links

- [Eclipse uProtocol Specification](https://github.com/eclipse-uprotocol/up-spec)
- [up-rust (Rust Implementation)](https://github.com/eclipse-uprotocol/up-rust)
- [PyO3 Documentation](https://pyo3.rs/)
- [Issue Tracker](https://github.com/eclipse-uprotocol/up-rust-py/issues)

## Acknowledgments

Built with:
- [Eclipse uProtocol](https://github.com/eclipse-uprotocol) - The underlying protocol specification
- [PyO3](https://pyo3.rs/) - Rust bindings for Python
- [Maturin](https://www.maturin.rs/) - Build tool for Rust/Python projects
