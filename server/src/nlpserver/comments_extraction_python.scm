([ 
    ;; The module docstring
    (
        module . 
            (expression_statement (string) @module.comment)
    )
    
    ;; docstring before function or docstring inside function or both
    (
       	(expression_statement (string) ? @function.outer_docstring) ?
        . 
        (function_definition
            name: ( identifier ) @function.name
            body: ( block
                (expression_statement . (string)? @function.inner_comment ) ?
                )?
            )
    )
    
    ;; comments before function or comments inside function or both
    (
        (comment) ? @function.outer_comment
        . 
        (function_definition
            name: ( identifier ) @function.name
            body: ( block
                (expression_statement . (string)? @function.inner_comment ) ?
                )?
            )
    )

    ;; Docstring before identifier
    (
        (expression_statement
            . (string) @docstring.with_identifier )
        . 
        (expression_statement
            . (assignment
                left: (identifier) @identifier.with_docstring
                right: _
                )
        )
    )

    ;; Comment before identifier
    (
        (comment) @comment.with_identifier
        .
        (expression_statement
            .(assignment
                left: (identifier) @identifier)
        )
    )

    ;; Lone comment (comment without identifier)
    (
        (comment) @lone.comment
        (expression_statement (assignment !left))
    )
    
    ;; Lone identifier (identifier without comment)
    ( 	(module 
        	(expression_statement (assignment left: (identifier) @lone.identifier))
        )
    )

    ;; all the comments, because lone comments couldn't be filtered
    (comment) @all_comments
])
