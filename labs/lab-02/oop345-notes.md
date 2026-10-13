# OOP345 — Dictionary Assignment: Technical Study Notes

Source: OOP345 Assignment #1 (Dictionary), provided by the student. The technical specifications below retain the original assignment wording for exact source quotations.

## Dictionary

This application loads a set of words from a file in `csv` format (comma separated values), stores them in memory, and performs some operations on them. The application will also measure the duration of certain operations, allowing the user to compare their performance. The time it takes to complete an operation will depend on the machine where the application is running; however, the relative difference in performance between various operation should hold regardless of the underlying hardware.

The input file will contain a large set of records; each record is stored on a single line in the format:

```
word,pos,definition
```

Where:

- `word` is the word being defined (might contain spaces).
- `pos` is the part of speech.
- `definition` is the definition of the word.

Put all the global variables, global functions/operator overloads, and types inside the `seneca` namespace.

### `tester_1` Module (supplied)

**Do not modify this module!** Study the code supplied and make sure you understand it.

### `settings` Module

The `settings` will contain functionality regarding configuration of the application. Design and code a structure named `Settings`; in the header, *declare* a global variable of this type named `g_settings` and define it in the implementation file.

For simplicity reasons, this type will contain only public data-members and no member-functions.

#### Public Members

- `m_show_all` as a Boolean attribute; when `true`, if a word has multiple definitions, all definitions should be printed on screen, otherwise only the first definition should be shown (default `false`).
- `m_verbose` as a Boolean attribute; when `true`, print to screen the part-of-speech of a word if it exists (default `false`).
- `m_time_units` as a `std::string` attribute; stores the time units to be used when printing duration of various operations. Possible values are `seconds`, `milliseconds`, `microseconds`, `nanoseconds` (default `nanoseconds`).

### `event` Module

Design and code a class named `Event` that stores information about a single event that happened during the execution of the program. At minimum, this class should store the name of the event (as a string) and its duration (as an object of type `std::chrono::nanoseconds`); add any other private members that your design requires.

#### Public Members

- a default constructor
- `Event(const char* name, const std::chrono::nanoseconds& duration)`: initializes the current instance with the values of the parameters.

#### Friend Helpers

- `operator<<`: inserts into the first parameter an object of type `Event` received as the second parameter, using the format:
  ```
  COUNTER: EVENT_NAME -> DURATION TIME_UNITS
  ```
  where
  - `COUNTER` is a *right aligned* field of size 2, that holds the number of times that this operator has been called (use a local-to-function variable that remains in memory for the lifetime of the program) **Do not use global/member variables to store the counter!**
  - `EVENT_NAME` is a *right aligned* field of size 40 with the name of the event
  - `DURATION` is a *right aligned* field with the duration of the event. The size of this field depends on the time units stored in the global settings:
    | **Time Units** | **Size of the field** |
    | -------------- | --------------------- |
    | Seconds        | 2                     |
    | Milliseconds   | 5                     |
    | Microseconds   | 8                     |
    | Nanoseconds    | 11                    |
  - `TIME_UNITS` a string representing the time units for displayed values

### `logger` Module

Design and code a class named `Logger` that manages a dynamically allocated collection of events *in the form of an array*. At minimum, this class should store the address of the array; add any other private members that your design requires.

This class will not support copy operations -- *disable them*.

#### Public Members

- default constructor
- destructor
- move operations
- `void addEvent(const Event& event)`: add to the array a copy of the event received as a parameter (resize the array if necessary).

#### Friend Helpers

- `operator<<`: inserts into the first parameter all the events stored in the logger received as the second parameter, using the format:
  ```
  EVENT<endl>
  EVENT<endl>
  ...
  ```

### `timeMonitor` Module

Design and code a class named `TimeMonitor` that is useful in measuring the duration of various operations/events. This class should use `chrono` library for time related operations. Add any private members that your design requires.

#### Public Members

- `void startEvent(const char* name)`: a new event with the `name` starts; records the time when the event started and the name of the event.
- `Event stopEvent()`: the current event started earlier by a call to `startEvent` has ended; take the time when it ended, calculate the duration of the event, create an instance of type `Event` and return it to the client.

### `dictionary` Module

Add to this module the following types:

```
enum class PartOfSpeech
{
  Unknown,
  Noun,
  Pronoun,
  Adjective,
  Adverb,
  Verb,
  Preposition,
  Conjunction,
  Interjection,
};
struct Word
{
  std::string m_word{};
  std::string m_definition{};
  PartOfSpeech m_pos = PartOfSpeech::Unknown;
};
```

Design and code a class named `Dictionary` that manages a dynamically allocated collection of objects of type `Word` *in the form of an array*. At minimum, this class should store the address of the array; add any other private members that your design requires.

#### Public Members

- default constructor
- `Dictionary(const char* filename)`: loads from the file specified as parameter the collection of words, allocate enough memory (but no more) for the array to store the data, and then load all the words into the array. If the file cannot be open, this function puts the current instance in an empty state.

  When loading the `pos` field from the file, only the following values are considered valid:
  | **Value found in file** | **Part of Speech**           |
  | ----------------------- | ---------------------------- |
  | `n.`                    | `PartOfSpeech::Noun`         |
  | `n. pl.`                | `PartOfSpeech::Noun`         |
  | `adv.`                  | `PartOfSpeech::Adverb`       |
  | `a.`                    | `PartOfSpeech::Adjective`    |
  | `v.`                    | `PartOfSpeech::Verb`         |
  | `v. i.`                 | `PartOfSpeech::Verb`         |
  | `v. t.`                 | `PartOfSpeech::Verb`         |
  | `v. t. & i.`            | `PartOfSpeech::Verb`         |
  | `prep.`                 | `PartOfSpeech::Preposition`  |
  | `pron.`                 | `PartOfSpeech::Pronoun`      |
  | `conj.`                 | `PartOfSpeech::Conjunction`  |
  | `interj.`               | `PartOfSpeech::Interjection` |
  Any other value found (or no value whatsoever) is considered to be `PartOfSpeech::Unknown`.
- `void searchWord(const char* word)`: searches in the collection of words the one specified as a parameter. If the word is found, print the definitions in the following format:
  ```
  WORD - (PART_OF_SPEECH) FIRST_DEFINITION<endl>
       - (PART_OF_SPEECH) SECOND_DEFINITION<endl>
       - (PART_OF_SPEECH) THIRD_DEFINITION<endl>
       ...
  ```
  Note that only for the first definition the `WORD` is printed; subsequent definitions are indented by the number of characters in the `WORD`.

  If in the global settings `m_show_all` is `false`, then the search stops after the first definition is found, subsequent definitions are ignored, and the function returns.

  If in the global settings `m_verbose` is `false` or the word has `PartOfSpeech::Unknown`, then `(PART_OF_SPEECH)` is not printed.

  If the word does not exist in the dictionary, then this function prints:
  ```
  Word 'WORD' was not found in the dictionary.<endl>
  ```

Add any other public **special** members that your design requires (without changing the specs above)!
