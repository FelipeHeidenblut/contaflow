import vm from 'node:vm'
import ts from 'typescript'

// Executa as ações reais do componente/store com rede e autenticação simuladas.
export const evaluate = (source, exports, dependencies) => {
  const compiled = ts.transpileModule(`${source}\nexport { ${exports} }`, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText
  const module = { exports: {} }
  vm.runInNewContext(compiled, {
    exports: module.exports,
    require: (name) => {
      if (!(name in dependencies)) throw new Error(`Unexpected dependency: ${name}`)
      return dependencies[name]
    },
  })
  return module.exports
}
