# Contribution Guide for Cloudwash

Thank you for your interest in contributing to **Cloudwash**! We welcome contributions from the community to help improve this tool for cloud resource cleanup. Please follow the guidelines below to ensure a smooth collaboration.

## How to Contribute

### 1. Fork and Clone the Repository
1. Fork the repository on GitHub: [Cloudwash Repository](https://github.com/RedHatQE/cloudwash)
2. Clone your fork to your local machine:
   ```sh
   git clone https://github.com/your-username/cloudwash.git
   cd cloudwash
   ```
3. Add the original repository as an upstream remote:
   ```sh
   git remote add upstream https://github.com/RedHatQE/cloudwash.git
   ```

### 2. Set Up Your Development Environment
Cloudwash requires Python and dependencies to be installed. Run the following to set up:
```sh
pip install -r requirements.txt
```

### 3. Create a Feature Branch
Always create a new branch for your changes:
```sh
git checkout -b feature-branch-name
```

### 4. Make Your Changes
- Follow best practices for coding and documentation.
  - Make sure your changes are consistent with the existing codebase.
- Write clean, maintainable, and well-commented code.
- Ensure changes align with Cloudwash's architecture and design principles.

### 5. Validate changes
Before submitting a PR, Validate the change works as expected and no regressions are introduced:

To validate the Feature or Bug fixes:
- You should populate the settings in a `settings.yaml` file in the root directory of the project. You can use the `settings.yaml.template` file as a reference to create your settings file.
- Or, You may also choose to populate settings in a conf directory for specific provider.

Refer the [User Guide](https://github.com/RedHatQE/cloudwash/blob/master/Docs/USER_GUIDE.md) for setting the environment and running the cleanup commands.

### 6. Commit Your Changes
Use clear and descriptive commit messages:
```sh
git add .
git commit -m "Feature|Bug|Doc: description of changes"
```

### 7. Push and Open a Pull Request
Push your changes to your fork:
```sh
git push origin feature-branch-name
```
Then, open a pull request (PR) against the `main` branch of the original Cloudwash repository.

### 8. Review and Feedback
- Your PR will be reviewed by maintainers.
- Address any requested changes.
- Once approved, your PR will be merged!

## Reporting Issues
If you encounter bugs or have feature suggestions, please open an issue [here](https://github.com/RedHatQE/cloudwash/issues).

---
Thank you for contributing to Cloudwash! 🚀
