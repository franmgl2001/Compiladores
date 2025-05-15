1. program -> declaration list
2. declaration_list -> {declaration}
3. declaration -> var-declaration | fun-declaration ;
4. var-declaration  -> type-specifier ID [ [ NUM ] ] ; ;
5. type-specifier  -> int | void ;
6. fun-declaration  -> type-specifier ID ( params ) compoud-stmt ;
7. params -> param-list | void
8. param-list -> param-l
9. param-list -> param { , param }
10. param  -> type-specifier ID [ [] ] ;
11. compound-stmt  -> { local-declarations statement-list } ;
12. local declaration ->{var-declaration};
13. statement-list  -> { statement } ;
14. statement ->  expression-stmt| compound-stmt| selection-stmt| iteration-stmt| return-stmt  ; 
15. expression-stmt ->  expression 
16. selection-stmt -> if ( expression ) statement [ else statement ] ;
17. iteration-stmt -> while ( expression ) statement ;
18. return-stmt -> return [expression ] ;
19. expression -> var = expression| simple-expression ;
20. var -> ID [ expression ]
21. simple-expression = additive-expression [ relop additive-expression ] ;
22. relop -> "<=" | "<" | ">" | ">=" | "==" | "!=" ;
23. additive-expression -> term { addop term } ;
24. addop ->  = "+" | "-" ;
25. term  -> factor { mulop factor } ;
26. mulop ->  "*" | "/" ;
27. factor -> ( expression ) | var | call | NUM ;
28. call  ->  ID (args) ;
29. arg -> expression { , expression } ;