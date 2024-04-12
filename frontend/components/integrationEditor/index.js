import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/router'
import dynamic from 'next/dynamic'

import Dropdown from 'react-bootstrap/Dropdown'
import Form from 'react-bootstrap/Form'

import 'react-image-crop/dist/ReactCrop.css'

const CodeEditor = dynamic(
  () => import('@uiw/react-textarea-code-editor').then((mod) => mod.default),
  { ssr: false }
)

import '@uiw/react-textarea-code-editor/dist.css'

const IntegrationEdtior = ({
  editorId = '',
  displayName = '',
  rules = [],
  value = '',
  placeholder = '',
  onChange = () => {},
}) => {
  const router = useRouter()

  const [selectionStart, setSelectionStart] = useState(0)

  const insertText = (textToInsert) => {
    let cursorPosition = selectionStart
    if (cursorPosition == 0) {
      let xmlEditor = document.getElementById(editorId + '-editor')
      cursorPosition = xmlEditor.selectionStart
    }
    let textBeforeCursorPosition = value.substring(0, cursorPosition)
    let textAfterCursorPosition = value.substring(cursorPosition, value.length)
    setSelectionStart(cursorPosition + textToInsert.length)
    let updatedValue =
      textBeforeCursorPosition + textToInsert + textAfterCursorPosition
    onChange({
      target: {
        value: updatedValue,
      },
    })
  }

  const addParsedResultClickHandler = (rule) => {
    let textToInsert = '{{ parsed_result["' + rule.name + '"] }}'
    insertText(textToInsert)
  }

  const addDocumentNameClickHandler = (e) => {
    let textToInsert = '{{ document.filename_without_extension }}'
    insertText(textToInsert)
  }

  const addDocumentExtensionClickHandler = (e) => {
    let textToInsert = '{{ document.extension }}'
    insertText(textToInsert)
  }

  const addCreatedDateClickHandler = (e) => {
    let textToInsert = '{{ builtin_vars["created_at"].strftime("%Y-%m-%d") }}'
    insertText(textToInsert)
  }

  const valueChangeHandler = (e) => {
    onChange({
      target: {
        value: e.target.value,
      },
    })
  }

  useEffect(() => {}, [])

  return (
    <Form.Group className="col-12" controlId="integrationEditor">
      <Form.Label>{displayName}</Form.Label>
      <div style={{ border: '1px solid #000', display: 'flex' }}>
        <Dropdown style={{ display: 'flex', flexDirection: 'row' }}>
          <Dropdown.Toggle
            id="dropdown"
            style={{
              fontSize: '80%',
              borderRadius: 0,
              borderRight: '1px solid #fff',
            }}
          >
            Add Parsed Results
          </Dropdown.Toggle>
          <Dropdown.Menu style={{ borderRadius: 0, padding: 0 }}>
            {rules.map((rule) => (
              <Dropdown.Item
                key={rule.id}
                style={{ fontSize: '80%' }}
                onClick={(e) => addParsedResultClickHandler(rule)}
              >
                {rule.name}
              </Dropdown.Item>
            ))}
          </Dropdown.Menu>
        </Dropdown>
        <Dropdown>
          <Dropdown.Toggle
            id="dropdown"
            style={{ fontSize: '80%', borderRadius: 0 }}
          >
            Add Document Properties
          </Dropdown.Toggle>
          <Dropdown.Menu style={{ borderRadius: 0, padding: 0 }}>
            <Dropdown.Item
              style={{ fontSize: '80%' }}
              onClick={(e) => addDocumentNameClickHandler(e)}
            >
              Document Name without Extension
            </Dropdown.Item>
            <Dropdown.Item
              style={{ fontSize: '80%' }}
              onClick={(e) => addDocumentExtensionClickHandler(e)}
            >
              Document Extension
            </Dropdown.Item>
            <Dropdown.Item
              style={{ fontSize: '80%' }}
              onClick={(e) => addCreatedDateClickHandler(e)}
            >
              Created Date
            </Dropdown.Item>
          </Dropdown.Menu>
        </Dropdown>
      </div>
      <CodeEditor
        id={editorId + '-editor'}
        value={value}
        language="js"
        placeholder={placeholder}
        onChange={(e) => valueChangeHandler(e)}
        onFocus={() => setSelectionStart(0)}
        padding={15}
        style={{
          border: '1px solid #333',
        }}
      />
    </Form.Group>
  )
}

export default IntegrationEdtior
