[   
    ;; The module comment
    (
        (translation_unit . 
            (comment) @module.comment)
    )
    
    ;; function outer comment and inner comment
    (
    	(comment) ? @function.outer_comment . 
          (function_definition
              body: (compound_statement .
                      (comment) @function.inner_comment
                     )
          ) 
    )
    
    ;; comment with declaration
    (
    	(comment) @comment_with_declaration
        .
        (declaration 
        	declarator: (init_declarator
             declarator: (identifier) @identifier_with_comment) )
    )
    
    ;; comment outside a struct
    (
    	(comment) @comment_with_struct
        	.
    	(struct_specifier
         name: (type_identifier) @struct_identifier )
    )
    
    ;; comments inside struct
    [
    	(field_declaration_list 
          (comment) @comment_inside_struct 
          . 
          (field_declaration
              declarator: (field_identifier) @field_identifier)
         )
         
         (field_declaration_list 
          (comment) @comment_inside_struct 
          . 
          (field_declaration
              declarator: (pointer_declarator
              		declarator: (field_identifier) @field_identifier
              	) 
              )
         )
     ]
]
