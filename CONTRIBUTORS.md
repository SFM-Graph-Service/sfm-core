# Contributors

## Core Contributors

### Garrick Dabbs
**Role**: Project Creator, Primary Developer, and Researcher
- Email: gdabbs@redhat.com
- GitHub: @gdabbs
- **Contributions**:
  - Project architecture and design
  - Research methodology and institutional economics domain expertise
  - Hayden SFM implementation and fidelity analysis
  - Framework bridges (Doughnut Economics, Ostrom SES/IAD)
  - Case study development and validation
  - All code review and quality assurance
  - Project direction and research applications

### Claude Sonnet 4.5
**Role**: AI Development Assistant
- Provider: Anthropic
- **Contributions**:
  - Code implementation assistance
  - Documentation generation and technical writing
  - Test suite development and test case design
  - API design and implementation suggestions
  - Performance optimization recommendations
  - Architectural pattern recommendations

**Attribution**: All commits include co-authorship:
```
Co-Authored-By: Garrick Dabbs <gdabbs@redhat.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## AI Assistance Disclosure

This project was developed with extensive assistance from **Claude AI** (Anthropic), specifically Claude Sonnet 4.5. AI assistance was used throughout code development, documentation, and testing.

**Human Oversight**: All AI-generated code and documentation was reviewed, validated, and iteratively refined by Garrick Dabbs. Design decisions, methodology interpretation, and project direction were human-driven.

**Verification**: Users should independently verify all outputs. Known limitations are documented in SFM_FIDELITY_ANALYSIS.md.

## Acknowledgments

**F. Gregory Hayden** - Creator of the Social Fabric Matrix methodology. This implementation is based on interpretation of his published work, particularly:

> Hayden, F. G. (2006). *Policymaking for a Good Society: The Social Fabric Matrix Approach to Policy Analysis and Program Evaluation*. Springer.

**Case Studies**: The validation examples (Nebraska K-12 education, low-level radioactive waste, corporate director networks, Clean Air Act) are based on Hayden's published research.

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](#contribution-guidelines) below.

### How to Contribute

1. **Report Issues**: Found a bug? Have a feature request? Open an issue on GitHub.
2. **Improve Documentation**: Documentation improvements are always appreciated.
3. **Submit Code**: Fork the repo, create a feature branch, and submit a pull request.
4. **Academic Feedback**: Especially valuable from institutional economics researchers and SFM practitioners.

### Contribution Guidelines

**Before Contributing:**
1. Check existing issues and pull requests to avoid duplicates
2. For major changes, open an issue first to discuss
3. Read the code of conduct below

**Code Standards:**
- Follow existing code style (Python 3.9+ compatible)
- Add tests for new features
- Update documentation for API changes
- Run test suite before submitting: `pytest tests/`
- Ensure CI passes (GitHub Actions)

**Pull Request Process:**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests: `pytest tests/`
5. Commit with clear messages: `git commit -m "Add feature X"`
6. Push to your fork: `git push origin feature/your-feature-name`
7. Open a pull request with description of changes

**What We're Looking For:**
- Bug fixes (see [open issues](https://github.com/SFM-Graph-Service/sfm-core/issues))
- Documentation improvements
- Performance optimizations
- New analysis methods
- Additional case study examples
- Improved Hayden methodology fidelity

### Code of Conduct

**Our Pledge:**
We are committed to providing a welcoming and harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

**Our Standards:**

**Positive behaviors:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors:**
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

**Enforcement:**
Instances of unacceptable behavior may be reported by contacting the project maintainer at gdabbs@redhat.com. All complaints will be reviewed and investigated and will result in a response deemed necessary and appropriate to the circumstances.

**Attribution:**
This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org/), version 1.4.

## Academic Use & Citation

If you use SFM Core in your research, please cite both:

1. **This software:**
   ```bibtex
   @software{sfm_core_2026,
     author = {Dabbs, Garrick},
     title = {SFM Core: Social Fabric Matrix Graph Service},
     year = {2026},
     url = {https://github.com/SFM-Graph-Service/sfm-core},
     version = {0.9.0},
     doi = {10.5281/zenodo.20418500}
   }
   ```

2. **Hayden's foundational work:**
   ```bibtex
   @book{hayden2006policymaking,
     author = {Hayden, F. Gregory},
     title = {Policymaking for a Good Society: The Social Fabric Matrix Approach to Policy Analysis and Program Evaluation},
     year = {2006},
     publisher = {Springer},
     isbn = {978-0-387-33812-8}
   }
   ```

**Zenodo DOI:** [![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20418500-blue)](https://doi.org/10.5281/zenodo.20418500)

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0). See the [LICENSE](LICENSE) file for details.

**In Brief:**
- ✅ Use for any purpose (academic, research, policy analysis)
- ✅ Modify and distribute
- ✅ Use in larger projects
- ⚠️  Must disclose source and license
- ⚠️  Must state changes made
- ⚠️  Derivative works must use GPL-3.0

## Questions?

- **Usage Questions**: Open a [GitHub Discussion](https://github.com/SFM-Graph-Service/sfm-core/discussions)
- **Bug Reports**: Open a [GitHub Issue](https://github.com/SFM-Graph-Service/sfm-core/issues)
- **Security Issues**: Email gdabbs@redhat.com (do not open public issue)
- **Academic Collaboration**: Email gdabbs@redhat.com

---

**Thank you to all contributors who help make SFM Core better!**
