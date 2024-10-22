# Table included as part of a list item

1. A list entry
1. Item with table

   {%
     include-markdown "./table.md"
   %}

1. Another list entry

## Expected output

1. A list entry
1. Item with table

   | A   | B   |
   | --- | --- |
   | foo | bar |

1. Another list entry
