# Contributing to BurnOut 3.0!!
<h3>Hello!👋</h3>
<p>Firstly, thank you so much for showing interest in BurnOut 3.0 and contributing to our project.👍</p>
The following are a set of guidelines for contributing to BurnOut. We are open to suggestions to enhance our project so feel free to propose changes to this document in a pull request.


### Table of contents
[Code of Conduct](#code-of-conduct)

[How Can I Contribute?](#how-can-i-contribute)
 * [Reporting Bugs](#reporting-bugs)
 * [Suggesting enhancements](#suggesting-enhancements)
 * [Pull Requests Methods](#pull-requests-methods)

[Style Guides](#style-guides)

[Need additional help?](#need-additional-help)

[References](#references)


### Code of Conduct
Everyone participating in this project needs to abide by the aPAS - A Personal Agile Scheduler Code of Conduct that can be found under the main repository link as a CODE_OF_CONDUCT.md file. By participating, you are expected to uphold this code. Please report unacceptable behavior to any of the original team members listed at the bottom of [README.md](README.md).

## How Can I Contribute?


  ## Reporting Bugs

  This section guides you through submitting a bug report for SE Group 26. 

  When you are creating a bug report, please ensure that you include as many details as possible to understand the issue.

  ## How Do I Submit A Bug Report?
   <p>Bugs are tracked as GitHub issues. After you've determined which repository your bug is related to, create an issue on that repository.
    Explain the problem and include additional details to help maintainers reproduce the problem:</p>
   <ul>
    <li><b>Use a clear and descriptive title</b> for the issue to identify the problem.</li>
    <li><b>Describe the exact steps which reproduce the problem in as many details as possible.</li></b>
    <li><b>Provide specific examples to demonstrate the steps.</b> Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those     examples. If you're providing snippets in the issue, use Markdown code blocks.</li>
    <li><b>If the problem is related to performance or memory, then ensure that you include a CPU profile capture with your report.</b></li>
    <li><b>Include screenshots and animated GIFs which show you following the described steps and clearly demonstrate the problem.</li></b>
    <li><b>If the problem wasn't triggered by a specific action</b>, describe what you were doing before the problem happened and share more information using the guidelines below.</li>
    </ul>
  
  ## Suggesting Enhancements
  This section guides you through submitting a suggestion for BurnOut, including completely new features and minor improvements to existing functionality. 

  Enhancement suggestions are tracked as GitHub issues. 
  After you've determined which repository your enhancement suggestion is related to, create an issue on that repository and provide the information like title, step-by-step description, specific examples.\
  Giving more detailed information will help us understand the suggestion better. 
  
  #### Provide details like 
  1) What is the enhancement? 
  2) Suggestions to implement the enhancement

  ## Pull Requests Methods
  The process described here has several goals: 

  - Maintain BurnOut 3.0 quality
  - Fix problems that are important to the users 
  - Engage the community in working towards the best possible BurnOut 
  - Enable a sustainable system for Atom's maintainers to review contributions

  Ensure that you follow the steps mentioned below in order to have your contribution reviewed by the maintainers:
  - Add a description of the modification.
  - Insert a clear and descriptive title.

### <h2>Style Guides</h2>

#### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* When only changing documentation, include `[ci skip]` in the commit title
* Consider starting the commit message with an applicable emoji:
    * :art: `:art:` when improving the format/structure of the code
    * :racehorse: `:racehorse:` when improving performance
    * :non-potable_water: `:non-potable_water:` when plugging memory leaks
    * :memo: `:memo:` when writing docs
    * :penguin: `:penguin:` when fixing something on Linux
    * :apple: `:apple:` when fixing something on macOS
    * :checkered_flag: `:checkered_flag:` when fixing something on Windows
    * :bug: `:bug:` when fixing a bug
    * :fire: `:fire:` when removing code or files
    * :green_heart: `:green_heart:` when fixing the CI build
    * :white_check_mark: `:white_check_mark:` when adding tests
    * :lock: `:lock:` when dealing with security
    * :arrow_up: `:arrow_up:` when upgrading dependencies
    * :arrow_down: `:arrow_down:` when downgrading dependencies
    * :shirt: `:shirt:` when removing linter warnings

#### CoffeeScript Styleguide

* Set parameter defaults without spaces around the equal sign
    * `clear = (count=1) ->` instead of `clear = (count = 1) ->`
* Use spaces around operators
    * `count + 1` instead of `count+1`
* Use spaces after commas (unless separated by newlines)
* Use parentheses if it improves code clarity.
* Prefer alphabetic keywords to symbolic keywords:
    * `a is b` instead of `a == b`
* Avoid spaces inside the curly-braces of hash literals:
    * `{a: 1, b: 2}` instead of `{ a: 1, b: 2 }`
* Include a single line of whitespace between methods.
* Capitalize initialisms and acronyms in names, except for the first word, which
  should be lower-case:
  * `getURI` instead of `getUri`
  * `uriToOpen` instead of `URIToOpen`
* Use `slice()` to copy an array
* Add an explicit `return` when your function ends with a `for`/`while` loop and
  you don't want it to return a collected array.
* Use `this` instead of a standalone `@`
  * `return this` instead of `return @`
* Place requires in the following order:
    * Built in Node Modules (such as `path`)
    * Local Modules (using relative paths)
* Place class properties in the following order:
    * Class methods and properties (methods starting with a `@`)
    * Instance methods and properties


#### Documentation Styleguide

* Use [Markdown](https://daringfireball.net/projects/markdown).
* Reference methods and classes in markdown with the custom `{}` notation:
    * Reference classes with `{ClassName}`
    * Reference instance methods with `{ClassName::methodName}`
    * Reference class methods with `{ClassName.methodName}`


## Git Commit Messages

  - Describe why any particular modification is being made.

  - Give a detailed description about the limitations of current code.

  - Use the imperative mood ("Move cursor to..." not "Moves cursor to...")

  - Limit the first line to 72 characters or less

  - Link an issue to the change

## Python Style Guides :

  All Python code is linted with Pylint. Ensure that before you commit any changes, your code passes all the default pylint checks. Pylint can be installed with
  `pip install pylint`.


### <h2>Need Additional Help?</h2>
<p>Due to any reason, if you feel like you have reservations related to the process, feel free to reach us out at [apatil25@ncsu.edu] Github process can be a bit complex and we don't want to lose your valuable contributions because of that reason. We are extremely glad that you have visited us and will make our project much better.</p>


## References
[Contributing.md](https://github.com/atom/atom/blob/master/CONTRIBUTING.md#specs-styleguide)