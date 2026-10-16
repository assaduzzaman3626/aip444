## tl;dr
This PR raises a new `MissingBoundaryException` instead of `AttributeError` when a multipart Content-Type lacks a boundary, and exports and documents it.

## Your Understanding
Your summary is broadly accurate. You correctly identify that the change replaces a less specific/less informative failure with a named exception (`MissingBoundaryException`) and that the tests verify the exception is reachable through more than one import path (`test_missing_boundary_exception_exports` checks `requests_toolbelt.MissingBoundaryException`, `multipart.MissingBoundaryException`, and both `__all__` lists). You were right to hedge with "introduces or exposes": the diff both defines the class in `requests_toolbelt/multipart/decoder.py` and exports it through the two `__init__.py` layers. Your statement that this helps developers identify the problem matches the PR description's motivation.

What you did not mention, and what the diff makes visible:
- The exception is raised *during construction*, before body parsing. The test `test_missing_boundary_fails_before_parsing_body` patches `MultipartDecoder._parse_body` and asserts `parse_body.assert_not_called()`. This ordering is a central claim of the PR description ("before body parsing").
- Only the *missing* boundary changes. Tests `test_empty_boundary_retains_body_parsing` and `test_recognised_boundary_decodes_content_and_headers` pin existing behaviour for explicit empty and duplicate boundaries, and `test_missing_content_type_keeps_existing_failure` shows a missing Content-Type still raises `AttributeError` rather than the new exception.
- The change is also a small backward-compatibility break, which the PR description's "Risk" section states: callers that previously caught `AttributeError` must now catch `MissingBoundaryException`.

Your "not understood" notes ("why the PR is not automated fully", "why some given URLs don't work") are not addressed by the supplied evidence. The PR description's "Unverified" section lists specific environments not run (full Tox, Windows full suite, macOS, PyPy, `noopenssl`, upstream CI) but does not explain a general policy; and no URLs are supplied in the material I was given. That is a genuine evidence gap rather than something the diff resolves. Your most important knowledge gap for this PR is how the new exception relates to the existing failure modes and to backward compatibility, since that is the substance of the change.

## Changes
- `requests_toolbelt/multipart/decoder.py`: defines `class MissingBoundaryException(Exception)` alongside the existing `NonMultipartContentTypeException` and documents it in the `MultipartDecoder` docstring. In `_find_boundary`, it now sets `self.boundary = None` before the parameter loop and, after the loop, raises `MissingBoundaryException('Missing boundary parameter in multipart Content-Type')` if `self.boundary is None`. Because a `boundary` parameter with an empty value sets `self.boundary` to a non-`None` empty bytes value, empty boundaries are not caught by this check — consistent with the empty-boundary regression tests.
- `requests_toolbelt/multipart/__init__.py` and `requests_toolbelt/__init__.py`: import the new exception and add it to each module's `__all__`, matching the pre-existing pattern for `ImproperBodyPartContentException` and `NonMultipartContentTypeException`.
- `docs/decoding-data.rst` (new) and `docs/index.rst`: add a documentation page using `autoclass`/`autoexception` for `MultipartDecoder` and the three decoder exceptions, and register it in the toctree.
- `HISTORY.rst` and `AUTHORS.rst`: changelog entry and author credit.
- `tests/test_multipart_decoder.py`: adds a parametrised `decode` fixture exercising both `MultipartDecoder(...)` and `MultipartDecoder.from_response(...)`, plus tests for missing, non-multipart, recognised, empty, and duplicate boundary cases, a `None` Content-Type case, an encoding case, and the export assertions.

Evidence-backed risks and gaps:
- Backward compatibility: the only behavioural guarantee changed is the exception type for a missing boundary; the PR description explicitly flags that `AttributeError` catchers must change. This is consistent with `self.boundary is None` triggering the new raise.
- The diff does not show the body of `from_response` or `_split_on_find`, so I cannot verify *how* `from_response` routes into `_find_boundary`; the fixture test implies it does, but the code path itself is outside the supplied diff. Likewise, behaviour for a `boundary` token with no `=` (e.g. `multipart/form-data; boundary` in the tests) depends on `_split_on_find`, which is not shown.
- The diff was not truncated, but repository context is still missing, so I make no claims about the rest of `decoder.py`.

## Discussion
The supplied PR description (author `ryanduguid`, 2026-10-07) states the intent: raise `MissingBoundaryException` in both `MultipartDecoder` and `from_response` before body parsing, export it through the public import layers, and document it, with "Closes #303." The description reports all 49 decoder tests passing on several Python versions, flake8 and docs Tox environments passing, and same-failure-on-master caveats for the full suite; these are author claims, not something I can verify from the diff, and no test output is included. The "Risk" section is the author's own acknowledged compatibility concern. The "Unverified" section lists environments the author says were not run.

No issue comments were supplied (`<issue_comments>` is empty), so I cannot summarise any reviewer or maintainer discussion; this should not be read as evidence that none exists. The referenced issue #303 is not included, so its contents are unknown.

## Learning
1. In `_find_boundary`, the code sets `self.boundary = None` and only raises after the loop completes — what distinguishes this from raising inside the loop the first time a boundary is not seen, and how do the empty-boundary tests depend on that distinction?
2. `test_missing_boundary_fails_before_parsing_body` patches `_parse_body` and asserts it was never called — what would a failing version of that test look like, and what does it tell you about where in object construction the new exception belongs?
3. The PR description's "Risk" section notes that callers catching `AttributeError` must now catch `MissingBoundaryException` — what kinds of calling code would be affected by that change, and why might a maintainer still consider the trade-off worthwhile?