# Security Policy

## Scope

This repository contains documentation, examples, and GitHub Actions workflow
templates for [claude-world.com](https://claude-world.com). It ships no package
or service, but people copy its code into their own projects, so we treat these
as security issues:

- An example or template that would introduce a vulnerability when used as
  documented (for example script injection in a workflow, a leaked token, or an
  unsafe permission default)
- A secret or credential committed to this repository
- A link that points to malicious or hijacked content

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest release and `main` | Yes |
| Older releases | No |

## Reporting a Vulnerability

Please report it privately:

1. **Do not** open a public GitHub issue for a suspected vulnerability.
2. Email **security@claude-world.com** with the affected file, what goes wrong,
   and how to reproduce it. Do not include live credentials.

We aim to acknowledge reports within 48 hours and will credit reporters in the
release notes unless you prefer otherwise.

## Using the Templates Safely

- Store API keys and tokens in GitHub Secrets, never in workflow files.
- Read a workflow before enabling it, and keep its `permissions:` minimal.
- Pass untrusted values (issue titles, comments, inputs) through `env:` rather
  than interpolating `${{ ... }}` into `run:` scripts.
