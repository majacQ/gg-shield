# Building OS packages

## Introduction

`ggshield` is written in Python, and this sometimes makes deployment complicated.

To solve those deployment issues, we provide standalone `ggshield` executables, that do not require a Python interpreter. This documentation explains how these executables are produced.

The process of generating the packages is handled by the `scripts/build-os-packages/build-os-packages` script. This script runs a series of "steps". It has a default list of steps, but you can tell it to run only specific steps using `scripts/build-os-packages/build-os-packages step1 step2...`.

All functions in the script starting with `step_` can be used as a step. This means you can get a list of all available steps with: `grep -o '^step_[a-z_]*' scripts/build-os-packages/build-os-packages`.

Here is a high-level overview of the main steps (square boxes are steps):

```mermaid
flowchart TD
    src[/source code/] --> build --> pyinstaller_dir[/"pyinstaller output
    (dist/ggshield)"/]
    pyinstaller_dir --> copy_files --> archive_dir[/"dir ready to be archived
    (packages/ggshield-$version-$target)"/]
    archive_dir --> test["test (run functional tests on archive dir)"]
    test --> signing{Called with --sign?} -->|yes| sign
    signing -->|no| create_archive
    sign --> create_archive --> pkg[/"pkg 🍏"/]
    create_archive --> zip[/"zip 🪟"/]
    create_archive --> tar.gz[/"tar.gz 🐧"/]
    create_archive --> deb[/"deb 🐧"/]
    create_archive --> rpm[/"rpm 🐧"/]
```

## Generating the standalone executable

We use [PyInstaller](https://pyinstaller.org) to generate `ggshield` standalone executable.

## Signing

MacOS and Windows archives are signed, but `build-os-packages` must be called with the `--sign` option to sign binaries because: signing requires access to secrets not available for PR from forks.

## macOS-specific information

For macOS, we produce a .pkg archive. The advantage of this file is that it can be installed by double-clicking on it or by using `sudo installer -pkg path/to/ggshield.pkg -target /`, and `ggshield` is immediately usable after install, without the need to alter `$PATH`.

### Inside the pkg

The .pkg itself installs `ggshield` files in `/opt/gitguardian/ggshield-$version` and a `ggshield` symbolic link in `/usr/local/bin/ggshield`.

### Setting up signing

When called with `--sign`, `build-os-packages` expects the following environment variables to be set:

- `$MACOS_P12_FILE`: Path to a signing certificate. You can export one from Xcode by following [Apple documentation][apple-signing-certificate].
- `$MACOS_P12_PASSWORD_FILE`: Path containing the password protecting the signing certificate. Xcode will ask for it when exporting it.
- `$MACOS_API_KEY_FILE`: Path to a JSON file holding the "App Store Connect API Key". This file is used by `rcodesign` for the notarization step. Follow [`rcodesign` documentation][rcodesign-api-key] to generate one.

Attention: these 3 files should be treated as secrets (even if `$MACOS_P12_FILE` is protected by a password).

[apple-signing-certificate]: https://help.apple.com/xcode/mac/current/#/dev154b28f09
[rcodesign-api-key]: https://gregoryszorc.com/docs/apple-codesign/0.27.0/apple_codesign_getting_started.html#obtaining-an-app-store-connect-api-key

### Signing implementation details

Although PyInstaller supports signing, it did not work at the time we tried it, so we use [rcodesign][] to do so.

`rcodesign` is a cross-platform CLI tool to sign, notarize and staple macOS binaries.

For Gatekeeper to accept the app, the executable and all the dynamic libraries must be signed, as well as the .pkg archive itself. Signing the executable and the libraries is done by the `sign` step, whereas signing the .pkg archive is done by the `create_archive` step.

[rcodesign]: https://gregoryszorc.com/docs/apple-codesign/

## Windows specific information

### Signing

We use [DigiCert](https://www.digicert.com) to sign `ggshield` Windows binaries.

#### Environment variables

On Windows, `build-os-packages` expects a number of environment variables to be set:

- `$WINDOWS_CERT_FINGERPRINT`: the thumbprint of the certificate.
- `$SM_API_KEY`: DigiCert API token.
- `$SM_HOST`: the host to use for DigiCert.
- `$SM_CLIENT_CERT_FILE`: the path to the signing user authentication certificate.
- `$SM_CLIENT_CERT_PASSWORD`: the password protecting the signing user authentication certificate.
- `$PATH`: `$PATH` must contain the path to:
  - the `signtool.exe` tool, from Microsoft
  - the `smctl.exe` tool, provided by DigiCert. Its default installation path is `C:\Program Files\DigiCert\DigiCert Keylocker Tools`.

#### Installing DigiCert tools

Downloading and installing DigiCert tools can be done with `scripts/build-os-packages/install-keylocker-tools`.

Note 1: `$SM_API_KEY` must be set to a valid API token: it is required to be able to download the tools.
Note 2: `install-keylocker-tools` expects `$PATH` to already contain the installation path of `smctl.exe`.

#### Building signed binaries

Once all environment variables are set and DigiCert tools are installed, one can build signed Windows binaries using `build-os-packages --sign`.
