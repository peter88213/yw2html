# yw2html - HTML export with custom templates from yWriter 7

For more information, see the [project homepage](https://peter88213.github.io/yw2html) with description and download instructions.


## Development

*yw2html* is organized as an Eclipse PyDev project. The official release branch on GitHub is *main*.

### Conventions

See https://github.com/peter88213/PyWriter/blob/main/docs/conventions.md

Exceptions:
- No localization is required.
- The directory structure is modified to minimize dependencies:

```
.
└── yw2html/
    ├── src/
    ├── test/
    └── tools/ 
        └── build.xml
```

### Development tools

- [Python](https://python.org) version 3.10
- [Eclipse IDE](https://eclipse.org) with [PyDev](https://pydev.org) and [EGit](https://www.eclipse.org/egit/)
- Apache Ant for building the application script

## Credits

- User *Hunter_71* presented the number to English conversion algorithm on [stack overflow](https://stackoverflow.com/a/51849443).
- User *Aristide* presented the integer to roman numeral conversion on [stack overflow](https://stackoverflow.com/a/47713392).

## License

yw2html is distributed under the [MIT License](http://www.opensource.org/licenses/mit-license.php).



