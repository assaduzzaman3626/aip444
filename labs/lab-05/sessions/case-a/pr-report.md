## tl;dr
This PR introduces a `MissingBoundaryException` to improve error handling in the `MultipartDecoder` when the multipart Content-Type lacks a recognized boundary.

## Your Understanding
You correctly recognized that this PR improves the code by adding functionality and increasing reliability. However, you expressed uncertainty about how these changes affect other parts of the program. This indicates a potential gap in understanding the broader impact of error handling changes, particularly regarding how exceptions propagate through the application and how other components may need to modify their error handling in response.

## Changes
1. **`AUTHORS.rst`**: A new author, Ryan Duguid, is added to the list of contributors at the end of the file.
   
2. **`HISTORY.rst`**: A note is added documenting the introduction of the `MissingBoundaryException`, explaining that this specific error will be raised instead of an `AttributeError` when there is no recognized boundary in a multipart Content-Type.

3. **`decoding-data.rst`**: This new file documents the functionality of the Multipart Decoder, including the newly introduced `MissingBoundaryException`. It explains that this exception will be raised during boundary detection issues.

4. **`index.rst`**: This file is updated to include a reference to the new documentation file for decoding data.

5. **`__init__.py`**: The `MissingBoundaryException` is imported and added to the public interface of the `requests_toolbelt` module, which makes it accessible for users of the library.

6. **`decoder.py`**: The new `MissingBoundaryException` class is defined to raise an error specifically when a multipart Content-Type lacks a boundary. The existing `_find_boundary` method is modified to raise this new exception if the boundary is not found.

7. **`test_multipart_decoder.py`**: Several tests are added or modified to ensure that the system raises `MissingBoundaryException` when there's no boundary. There are tests to ensure that recognized boundaries still function correctly and that non-multipart content types raise the appropriate error (`NonMultipartContentTypeException`).

These changes together reinforce error handling and clear messaging for users of `MultipartDecoder`, which enhances robustness. The risk is highlighted that callers catching the `AttributeError` must now catch the new `MissingBoundaryException`.

## Discussion
The PR was created to address issue #303, aiming to improve the error handling within `MultipartDecoder` when the boundary is missing. The author notes that after the implementation, all decoder tests passed across multiple Python versions and platforms, ensuring compatibility. The coverage includes various edge cases related to the boundaries, thus improving reliability. The author also points out risks: if other parts of the program relied on catching `AttributeError`, updates will be needed to accommodate the new exception.

No issue comments were provided for further discussion.

## Learning
1. How will the introduction of `MissingBoundaryException` affect existing error-handling practices in the parts of the application that utilize `MultipartDecoder`?
2. What steps should be taken to ensure that users of the library are aware of this exception and its implications?
3. How does the change in exception type from `AttributeError` to `MissingBoundaryException` impact legacy code that might not expect this new error?