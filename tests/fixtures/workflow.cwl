cwlVersion: v1.2
$graph:
  - class: Workflow
    id: hello
    inputs:
      message:
        type: string
        default: Hello world
    outputs:
      result:
        type: File
        outputSource: echo/result
    steps:
      echo:
        run: '#echo'
        in:
          message: message
        out: [result]
  - class: CommandLineTool
    id: echo
    baseCommand: echo
    inputs:
      message:
        type: string
        inputBinding:
          position: 1
    stdout: message.txt
    outputs:
      result:
        type: stdout
$namespaces:
  s: https://schema.org/
s:name: Hello
s:description: A minimal template-generation example.
s:dateCreated: '2026-09-18'
s:license: https://spdx.org/licenses/Apache-2.0
s:softwareVersion: '0.1.0'
s:softwareHelp:
  s:name: User guide
  s:url: https://example.org/hello
s:publisher:
  s:name: Example Organization
s:author:
  s:givenName: Example
  s:familyName: Author
  s:email: author@example.org
  s:affiliation:
    s:name: Example Organization
