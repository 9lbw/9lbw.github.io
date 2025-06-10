---
title: "Linux sucks, I love it"
date: "2025-06-10"
description: "Or more accurately, how I learned to love Gentoo"
---

I love Linux. I do. But I hate it. A lot. Sometimes at least. But why? How could anyone hate the crown jewel of open-source software? Well, I don’t. I hate the ecosystem around it. I hate the distributions. I hate the compromises.

## Binaries, binaries, and binaries
Let’s start with a quick crash course in package managers. In the Unix/Linux world, there are two types of package managers. Binary-based ones and Source-based ones. Binary-based package managers pull in precompiled binaries from some officially curated repository that's hosted somewhere. Let's take Void Linux for example.

When you install a package on Void Linux using `xbps-install firefox`, you're downloading a precompiled binary that was built on the maintainer's build servers with their chosen compile flags, optimizations, and feature sets. This is fast, convenient, and works for 99% of users. But here's the problem: those binaries weren't built for *your* system.

## The binary build factory

Most binary-based distributions rely on massive automated build systems. Debian has their buildd network, hundreds of machines constantly churning out packages. Ubuntu uses Launchpad's build farm. Arch Linux has their build servers. These systems work something like this:

1. A maintainer pushes a package update to the repository
2. The build system automatically detects the change
3. Virtual machines or containers spin up with a clean, minimal environment
4. The package gets compiled with distribution-wide default settings
5. The resulting binary gets signed and pushed to mirrors worldwide

These build farms are optimized for one thing: producing binaries that work on as many systems as possible. That means compiling for the lowest common denominator CPU (usually x86_64 baseline), enabling every optional feature that users might want, and using the most stable compiler flags.

You might have the newest, fanciest CPU from Intel with AVX512 support, but your binary distro will never let you reap the benefits of that. Neither do you get the opportunity to not compile parts of a package you don't need. Let's set the stage: You use Void with Sway, meaning that you use Wayland. You want to install Firefox, or MPV, or any other package that offers support for both X(11) and Wayland. You don't *need* the X(11) support, so why should you keep it in the package? Well, you sadly cannot just go "I don't want X support" with a binary-based package manager. Remember, the lowest common denominator is still X, not Wayland.

## The antidote: Portage
You saw this coming, maybe, hopefully. Gentoo here is the perfect antidote. Portage, the package manager used by Gentoo, is source-based, meaning that instead of pulling in precompiled binaries, you get the source code of the package you want to install and an ebuild, a text file that can be compared to a Makefile, instead.
When you run emerge firefox on Gentoo, here's what happens behind the scenes:

1. Portage downloads the Firefox source code (all 200+ MB of it).
2. It reads the ebuild file, which contains instructions for how to compile Firefox
3. It checks your system's USE flags - these are compile-time options that determine what features get built
4. It configures the build process based on your CPU architecture, compiler flags, and system configuration
5. It compiles Firefox specifically for your machine
6. Finally, it installs the resulting binary

This process can take anywhere from a few minutes for small utilities to several hours (depending on your machine) for massive packages like Firefox or LibreOffice.

## USE Flags
This is where Gentoo really shines. USE Flags are compile-time switches that let you decide exactly what gets built into each package. You can define them globally in your `make.conf` or locally inside the `package.use` folder. Don't need Bluetooth because your motherboard doesn't have it? -bluetooth. You have an AMD GPU? Add `VIDEO_CARDS="amdgpu"` to your make.conf.