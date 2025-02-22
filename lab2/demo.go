package main

import (
	"fmt"
	"go/ast"
	"go/format"
	"go/parser"

	//"go/printer"
	"go/token"
	"os"
)

func insertIntVar(file *ast.File, name string, value int) {
	var before, after []ast.Decl

	if len(file.Decls) > 0 {
		hasImport := false
		if genDecl, ok := file.Decls[0].(*ast.GenDecl); ok {
			hasImport = genDecl.Tok == token.IMPORT
		}

		if hasImport {
			before, after = []ast.Decl{file.Decls[0]}, file.Decls[1:]
		} else {
			after = file.Decls
		}
	}

	file.Decls = append(before,
		&ast.GenDecl{
			Tok: token.VAR,
			Specs: []ast.Spec{
				&ast.ValueSpec{
					Names: []*ast.Ident{ast.NewIdent(name)},
					Type:  ast.NewIdent("int"),
					Values: []ast.Expr{
						&ast.BasicLit{
							Kind:  token.INT,
							Value: fmt.Sprintf("%d", value),
						},
					},
				},
			},
		},
	)
	file.Decls = append(file.Decls, after...)
}

func insertHello(file *ast.File) {
	ast.Inspect(file, func(node ast.Node) bool {
		if ifStmt, ok := node.(*ast.IfStmt); ok {
			ifStmt.Body.List = append(
				[]ast.Stmt{
					&ast.ExprStmt{
						X: &ast.CallExpr{
							Fun: &ast.SelectorExpr{
								X:   ast.NewIdent("fmt"),
								Sel: ast.NewIdent("Printf"),
							},
							Args: []ast.Expr{
								&ast.BasicLit{
									Kind:  token.STRING,
									Value: "\"hello\"",
								},
							},
						},
					},
				},
				ifStmt.Body.List...,
			)
		}
		return true
	})
}
func revriteVar(file *ast.File) {
	// Стек для отслеживания родительских нод

	ast.Inspect(file, func(node_ ast.Node) bool {
		if BlockStmt, ok := node_.(*ast.BlockStmt); ok {
			for _, node := range BlockStmt.List {
				// Проверяем, является ли узел объявлением (GenDecl)
				if DeclStmt, ok := node.(*ast.DeclStmt); ok {
					genDecl := DeclStmt.Decl.(*ast.GenDecl)
					// Проверяем, является ли объявление var
					if genDecl.Tok == token.VAR {
						// Получаем родительскую ноду (если она есть)

						// Проверяем каждую спецификацию
						for _, spec := range genDecl.Specs {
							if valueSpec, ok := spec.(*ast.ValueSpec); ok {
								// Если переменных больше одной
								if len(valueSpec.Names) > 1 {
									fmt.Printf("Родительская нода для GenDecl: %T\n", BlockStmt)
									fmt.Printf("Найдено объявление var с множественной инициализацией:\n")
									fmt.Printf("  Переменные: %v\n", valueSpec.Names)

									new_specs := make([]ast.Stmt, len(valueSpec.Names))

									for i, name := range valueSpec.Names {
										var value ast.Expr
										if len(valueSpec.Values) > 0 {
											value = valueSpec.Values[i]
											new_specs[i] = &ast.DeclStmt{
												Decl: &ast.GenDecl{
													Tok: token.VAR,
													Specs: []ast.Spec{
														&ast.ValueSpec{
															Names:  []*ast.Ident{name},
															Type:   valueSpec.Type,
															Values: []ast.Expr{value},
														},
													},
												}}
										} else {
											new_specs[i] = &ast.DeclStmt{
												Decl: &ast.GenDecl{
													Tok: token.VAR,
													Specs: []ast.Spec{
														&ast.ValueSpec{
															Names:  []*ast.Ident{name},
															Type:   valueSpec.Type,
															Values: nil,
														},
													},
												}}
										}

									}
									for _, smt := range new_specs {
										fmt.Println(smt)
									}
									fmt.Println("====")
									for _, smt := range BlockStmt.List {
										fmt.Println(smt, "==", node, "res ", smt != node)
										if smt != node {
											new_specs = append(new_specs, smt)
										}
									}
									for _, smt := range BlockStmt.List {
										fmt.Println(smt)
									}

									BlockStmt.List = new_specs
									fmt.Println("====")
									for _, smt := range new_specs {
										fmt.Println(smt)
									}
									if valueSpec.Type != nil {
										fmt.Printf("  Тип: %s\n", valueSpec.Type)
									}
									if len(valueSpec.Values) > 0 {
										fmt.Printf("  Значения: %v\n", valueSpec.Values)
									}
									fmt.Println()
								}
							}
						}
					}
				}
			}
		}

		return true
	})
}

func main() {
	if len(os.Args) != 2 {
		return
	}

	fset := token.NewFileSet()
	if file, err := parser.ParseFile(fset, os.Args[1], nil, parser.ParseComments); err == nil {
		//insertIntVar(file, "xxx", 666)
		//insertHello(file)
		revriteVar(file)
		if format.Node(os.Stdout, fset, file) != nil {
			fmt.Printf("Formatter error: %v\n", err)
		}
		//ast.Fprint(os.Stdout, fset, file, nil)
	} else {
		fmt.Printf("Errors in %s\n", os.Args[1])
	}
}
