<div align="center">

<h1 align="center">
  SNIPER: Project Initializer
</h1>

<p align="center">
  A powerful and interactive tool to bootstrap new software projects from dynamic, professional templates.
</p>

<p align="center">
  <a href="https://github.com/limearch/sniper">
    <img src="https://img.shields.io/badge/Part%20of-SNIPER%20Toolkit-magenta?style=for-the-badge" alt="Part of SNIPER Toolkit">
  </a>
  <img src="https://img.shields.io/badge/Language-Python-blue?style=for-the-badge" alt="Language">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge" alt="License">
</p>

</div>

---

**`sniper-project-init`** (or `sniper-init`) embodies the SNIPER philosophy of **precision, speed, and integration**. It's not just a file copier; it's an intelligent engine that automates the tedious setup process, allowing developers to go from an idea to coding in seconds.

Whether you're starting a Flask API, a Go CLI tool, or a React frontend, `sniper-init` provides a solid, production-ready foundation.

## 🎯 Core Philosophy

-   **Template-Driven Intelligence**: The core tool is lean and generic. All the logic, questions, and setup commands are defined within the templates themselves via a `sniper.json` manifest.
-   **Interactive First**: A beautiful and intuitive interactive mode guides you through the setup process, making it perfect for exploration and daily use.
-   **Automation Ready**: A powerful direct (non-interactive) mode allows for scripting and automating project creation, ideal for CI/CD or development scripts.
-   **Maximum Extensibility**: Adding a new, complex project template is as simple as creating a new folder with a manifest file. No changes to the core tool are needed.

## ✨ Features

-   **Interactive Wizard**: A user-friendly, `questionary`-based interface for a smooth setup experience.
-   **Rich UI**: Beautifully formatted help screens, summaries, and status indicators powered by `rich`, matching the SNIPER aesthetic.
-   **Dynamic Templates**: Templates can define their own questions, which are then asked dynamically during the interactive session.
-   **Post-Creation Hooks**: Automatically run shell commands after project creation (e.g., `git init`, `npm install`, `go mod init`).
-   **Jinja2 Templating Engine**: Use the power of Jinja2 inside your template files to insert project names, versions, descriptions, and more.
-   **Docker Integration**: Interactively choose to include `Dockerfile` and `docker-compose.yml` files for container-ready projects.
-   **Custom Template Support**: Easily point the tool to your own directory of custom, private templates.

---

## 🚀 Quick Start

`sniper-init` is installed as part of the main **SNIPER Toolkit**. Ensure you have run the main `install.sh` script first.

### 1. Interactive Mode (Recommended)

For the best experience, run the command without any arguments to launch the interactive wizard.

```bash
sniper-init
```

The tool will guide you through the following steps:
1.  **Enter Project Name**: The name of your new project directory.
2.  **Select Project Type**: Choose from the list of available templates.
3.  **Answer Template-Specific Questions**: Provide values for description, version, etc.
4.  **Choose Options**: Decide whether to initialize Git, include Docker files, and select a license.

### 2. Direct Mode (For Automation)

You can also create a project with a single command, which is perfect for scripting.

```bash
# Syntax: sniper-init <project-name> -t <template> [options]

# Example: Create a Go CLI tool
sniper-init my-cli-app -t go-cli

# Example: Create a React project without Git
sniper-init my-react-site -t react-ts-vite --no-git
```

---

## 🛠️ Available Templates

This tool comes with a suite of professional, production-ready templates out of the box:

| Template Name        | Language/Framework | Key Features                                    |
| -------------------- | ------------------ | ----------------------------------------------- |
| `flask-api`          | Python (Flask)     | Modular structure, Blueprints, Docker, `.env`   |
| `django-project`     | Python (Django)    | Official `django-admin` bootstrap, Docker       |
| `express-api`        | Node.js (Express)  | Modular routes, `nodemon` for dev, Docker       |
| `react-ts-vite`      | JavaScript (React) | TypeScript, bootstrapped with Vite, Docker      |
| `nextjs-app-router`  | JavaScript (Next.js)| Official bootstrap, App Router, Tailwind CSS  |
| `c-project`          | C                  | `Makefile`, `src`/`include` structure, `build` dir|
| `cpp-project`        | C++                | Modern C++17 `Makefile`, class structure        |
| `go-cli`             | Go                 | `cmd`/`internal` layout, `go.mod` init, Docker  |
| `web-static`         | HTML/CSS/JS        | Simple, clean structure for static websites     |

---

## 🔧 Creating Your Own Templates

The power of `sniper-init` lies in its simplicity. To create a new template, just follow these steps:

1.  **Create a Directory**: Inside the `templates/` folder (or your custom templates directory), create a new folder (e.g., `rust-cli`).

2.  **Create `sniper.json`**: This is the manifest file that controls everything.

    ```json
    // templates/rust-cli/sniper.json
    {
      "name": "Rust CLI Application",
      "description": "A CLI tool built with Rust and Cargo.",
      "questions": [
        {
          "key": "project_description",
          "prompt": "Enter a description for your Rust CLI:",
          "default": "A new Rust application."
        }
      ],
      "post_init_commands": [
        {
          "command": "cargo init --name {{ project_name }}",
          "message": "Initializing Rust project with Cargo..."
        }
      ],
      "next_steps": [
        "cd {{ project_name }}",
        "cargo run"
      ]
    }
    ```

3.  **Add Template Files**: Add any other files you need. You can use Jinja2 syntax inside them.

    ```rust
    // templates/rust-cli/src/main.rs (EXAMPLE - Cargo creates this)
    fn main() {
        // The project description is "{{ project_description }}"
        println!("Hello from {{ project_name }}!");
    }
    ```

That's it! The next time you run `sniper-init`, your "rust-cli" template will appear as an option.

---

## ⚙️ Configuration

You can configure `sniper-init` by editing the main `sniper-config.json` file or using the `configer` tool. A key option is setting a path to your own templates directory:

```bash
# Tell sniper-init to also look for templates in ~/my-templates
configer set project_init custom_templates_dir "/home/user/my-templates"
```
