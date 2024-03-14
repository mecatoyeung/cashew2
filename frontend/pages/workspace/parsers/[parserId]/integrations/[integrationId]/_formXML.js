import { useState, useEffect, useRef, useMemo, useCallback } from "react"
import { useRouter } from "next/router"
import dynamic from "next/dynamic";
import Image from "next/image"

import { produce } from "immer"

import { Form } from "react-bootstrap"
import { Modal } from "react-bootstrap"
import { Button } from "react-bootstrap"
import { Dropdown } from "react-bootstrap"
import { Accordion } from "react-bootstrap"

import Select from "react-select"

import WorkspaceLayout from "../../../../../../layouts/workspace"

import service from "../../../../../../service"

import "@uiw/react-textarea-code-editor/dist.css";
import integrationsStyles from "../../../../../../styles/Integrations.module.css"

import IntegrationEdtior from "../../../../../../components/integrationEditor";

export default function XMLForm(props) {
  const router = useRouter();

  const { parserId, integrationId } = router.query

  const [xmlPathSelectionStart, setXmlPathSelectionStart] = useState(0)
  const [templateSelectionStart, setTemplateSelectionStart] = useState(0)

  const [form, setForm] = useState({
    name: "",
    integrationType: "XML_INTEGRATION",
    xmlPath: "",
    template: "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
    intervalSeconds: 15,
    activated: true,
    errorMessage: "",
  });

  const [rules, setRules] = useState([])

  const getRules = () => {
    if (!parserId) return
    service.get(`rules/?parserId=${parserId}`, response => {
      setRules(response.data)
    })
  }

  const addBtnClickHandler = () => {
    let errorMessage = "";
    if (form.name.trim() == "") {
      errorMessage = "Integration name should not be empty.";
    }
    if (form.xmlPath.trim() == "") {
      errorMessage = "XML path should not be empty.";
    }
    setForm(
      produce((draft) => {
        draft.errorMessage = errorMessage;
      })
    );
    if (errorMessage) {
      return;
    }
    service.post(
      "/integrations/",
      {
        parser: parserId,
        integrationType: form.integrationType,
        name: form.name,
        xmlPath: form.xmlPath,
        template: form.template,
        intervalSeconds: form.intervalSeconds,
        activated: form.activated,
      },
      (response) => {
        router.push("/workspace/parsers/" + parserId + "/integrations/");
      }
    );
  };

  const backBtnClickHandler = () => {
    router.push("/workspace/parsers/" + parserId + "/integrations/");
  };

  const saveBtnClickHandler = () => {
    service.put(
      "/integrations/" + integrationId + "/",
      {
        parser: parserId,
        integrationType: form.integrationType,
        name: form.name,
        xmlPath: form.xmlPath,
        template: form.template,
        intervalSeconds: form.intervalSeconds,
        activated: form.activated,
      },
      (response) => {
        router.push("/workspace/parsers/" + parserId + "/integrations/");
      }
    );
  }

  const xmlPathChangeHandler = (e) => {
    setXmlPathSelectionStart(0)
    e.target.value = e.target.value.replace(/[\r\n]+/g, " ");
    setForm(
      produce((draft) => {
        draft.xmlPath = e.target.value
      })
    )
  }

  const templateChangeHandler = (e) => {
    setTemplateSelectionStart(0)
    setForm(
      produce((draft) => {
        draft.template = e.target.value;
      })
    )
  }

  const addParsedResultClickHandlerInTemplate = (e, rule) => {
    let textToInsert = "{{ parsed_result[\"" + rule.name + "\"] }}"
    let cursorPosition = templateSelectionStart
    if (cursorPosition == 0) {
      let templateEditor = document.getElementById("template-editor")
      cursorPosition = templateEditor.selectionStart
    }
    let textBeforeCursorPosition = form.template.substring(0, cursorPosition)
    let textAfterCursorPosition = form.template.substring(cursorPosition, form.template.length)
    setTemplateSelectionStart(cursorPosition + textToInsert.length)
    setForm(
      produce((draft) => {
        draft.template = textBeforeCursorPosition + textToInsert + textAfterCursorPosition
      }))
  }

  const addDocumentNameClickHandlerInTemplate = (e) => {
    let textToInsert = "{{ document.filename_without_extension }}"
    let cursorPosition = templateSelectionStart
    if (cursorPosition == 0) {
      let templateEditor = document.getElementById("template-editor")
      cursorPosition = templateEditor.selectionStart
    }
    let textBeforeCursorPosition = form.template.substring(0, cursorPosition)
    let textAfterCursorPosition = form.template.substring(cursorPosition, form.template.length)
    setTemplateSelectionStart(cursorPosition + textToInsert.length)
    setForm(
      produce((draft) => {
        draft.template = textBeforeCursorPosition + textToInsert + textAfterCursorPosition
      }))
  }

  const addDocumentExtensionClickHandlerInTemplate = (e) => {
    let textToInsert = "{{ document.extension }}"
    let cursorPosition = templateSelectionStart
    if (cursorPosition == 0) {
      let templateEditor = document.getElementById("template-editor")
      cursorPosition = templateEditor.selectionStart
    }
    let textBeforeCursorPosition = form.template.substring(0, cursorPosition)
    let textAfterCursorPosition = form.template.substring(cursorPosition, form.template.length)
    setTemplateSelectionStart(cursorPosition + textToInsert.length)
    setForm(
      produce((draft) => {
        draft.template = textBeforeCursorPosition + textToInsert + textAfterCursorPosition
      }))
  }

  const addCreatedDateClickHandlerInXmlPath =(e) => {
    let textToInsert = "{{ builtin_vars[\"created_at\"].strftime(\"%Y-%m-%d\") }}"
    let cursorPosition = xmlPathSelectionStart
    if (cursorPosition == 0) {
      let xmlPathEditor = document.getElementById("xmlPath-editor")
      cursorPosition = xmlPathEditor.selectionStart
    }
    let textBeforeCursorPosition = form.xmlPath.substring(0, cursorPosition)
    let textAfterCursorPosition = form.xmlPath.substring(cursorPosition, form.xmlPath.length)
    setXmlPathSelectionStart(cursorPosition + textToInsert.length)
    setForm(
      produce((draft) => {
        draft.xmlPath = textBeforeCursorPosition + textToInsert + textAfterCursorPosition
      }))
  }

  const addParsedResultClickHandlerInXmlPath = (e, rule) => {
    let textToInsert = "{{ parsed_result[\"" + rule.name + "\"] }}"
    let cursorPosition = xmlPathSelectionStart
    if (cursorPosition == 0) {
      let xmlPathEditor = document.getElementById("xmlPath-editor")
      cursorPosition = xmlPathEditor.selectionStart
    }
    let textBeforeCursorPosition = form.xmlPath.substring(0, cursorPosition)
    let textAfterCursorPosition = form.xmlPath.substring(cursorPosition, form.xmlPath.length)
    setXmlPathSelectionStart(cursorPosition + textToInsert.length)
    setForm(
      produce((draft) => {
        draft.xmlPath = textBeforeCursorPosition + textToInsert + textAfterCursorPosition
      }))
  }

  const addDocumentNameClickHandlerInXmlPath = (e) => {
    let textToInsert = "{{ document.filename_without_extension }}"
    let cursorPosition = xmlPathSelectionStart
    if (cursorPosition == 0) {
      let xmlPathEditor = document.getElementById("xmlPath-editor")
      cursorPosition = xmlPathEditor.selectionStart
    }
    let textBeforeCursorPosition = form.xmlPath.substring(0, cursorPosition)
    let textAfterCursorPosition = form.xmlPath.substring(cursorPosition, form.xmlPath.length)
    setXmlPathSelectionStart(cursorPosition + textToInsert.length)
    setForm(
      produce((draft) => {
        draft.xmlPath = textBeforeCursorPosition + textToInsert + textAfterCursorPosition
      }))
  }

  const addDocumentExtensionClickHandlerInXmlPath = (e) => {
    let textToInsert = "{{ document.extension }}"
    let cursorPosition = xmlPathSelectionStart
    if (cursorPosition == 0) {
      let xmlPathEditor = document.getElementById("xmlPath-editor")
      cursorPosition = xmlPathEditor.selectionStart
    }
    let textBeforeCursorPosition = form.xmlPath.substring(0, cursorPosition)
    let textAfterCursorPosition = form.xmlPath.substring(cursorPosition, form.xmlPath.length)
    setXmlPathSelectionStart(cursorPosition + textToInsert.length)
    setForm(
      produce((draft) => {
        draft.xmlPath = textBeforeCursorPosition + textToInsert + textAfterCursorPosition
      }))
  }

  const addCreatedDateClickHandlerInTemplate =(e) => {
    let textToInsert = "{{ builtin_vars[\"created_at\"].strftime(\"%Y-%m-%d\") }}"
    let cursorPosition = templateSelectionStart
    if (cursorPosition == 0) {
      let xmlPathEditor = document.getElementById("template-editor")
      cursorPosition = xmlPathEditor.selectionStart
    }
    let textBeforeCursorPosition = form.template.substring(0, cursorPosition)
    let textAfterCursorPosition = form.template.substring(cursorPosition, form.template.length)
    setTemplateSelectionStart(cursorPosition + textToInsert.length)
    setForm(
      produce((draft) => {
        draft.template = textBeforeCursorPosition + textToInsert + textAfterCursorPosition
      }))
  }

  useEffect(() => {
    if (props.type == "edit") {
      setForm(
        produce((draft) => {
          draft.id = props.integration.id
          draft.name = props.integration.name
          draft.integrationType = props.integration.integrationType
          draft.parser = props.integration.parser
          draft.xmlPath = props.integration.xmlPath
          draft.template = props.integration.template
          draft.pdfIntegrationType = props.integration.pdfIntegrationType
          draft.preProcessing = props.integration.preProcessing
          draft.postProcessing = props.integration.postProcessing
          draft.pdfPath = props.integration.pdfPath
          draft.intervalSeconds = props.integration.intervalSeconds,
          draft.activated = props.integration.activated
        })
      );
    }
    if (parserId != null) {
      getRules()
    }
  }, [parserId]);

  return (
    <WorkspaceLayout>
      <div className={integrationsStyles.wrapper}>
        {props.type == "add" && (
          <h1 className={integrationsStyles.h1}>Add XML Integration</h1>
        )}
        {props.type == "edit" && (
          <h1 className={integrationsStyles.h1}>Edit XML Integration</h1>
        )}
        <Accordion defaultActiveKey="0" style={{ padding: 10 }}>
          <Accordion.Item eventKey="0">
            <Accordion.Header>Please fill in the form</Accordion.Header>
            <Accordion.Body>
              <Form>
                <Form.Group className="col-12" controlId="addForm.integrationName">
                  <Form.Label>Integration Name</Form.Label>
                  <Form.Control
                    type="name"
                    placeholder="Integration Name"
                    value={form.name}
                    onChange={(e) => {
                      setForm(
                        produce((draft) => {
                          draft.name = e.target.value;
                        })
                      );
                    }}
                  />
                </Form.Group>
                {/*<Form.Group className="col-12" controlId="addForm.xmlPath">
                  <Form.Label>XML Path</Form.Label>
                  <div style={{ border: "1px solid #000", display: "flex" }}>
                    <Dropdown style={{ display: "flex", flexDirection: "row"}}>
                      <Dropdown.Toggle id="dropdown" style={{ fontSize: "80%", borderRadius: 0, borderRight: "1px solid #fff" }}>
                        Add Parsed Results
                      </Dropdown.Toggle>
                      <Dropdown.Menu style={{ borderRadius: 0, padding: 0 }}>
                        {rules.map(rule => (
                          <Dropdown.Item key={rule.id} style={{ fontSize: "80%" }} onClick={(e) => addParsedResultClickHandlerInXmlPath(e, rule)}>{rule.name}</Dropdown.Item>
                        ))}
                      </Dropdown.Menu>
                    </Dropdown>
                    <Dropdown>
                      <Dropdown.Toggle id="dropdown" style={{ fontSize: "80%", borderRadius: 0 }}>
                        Add Document Properties
                      </Dropdown.Toggle>
                      <Dropdown.Menu style={{ borderRadius: 0, padding: 0 }}>
                        <Dropdown.Item style={{ fontSize: "80%" }} onClick={(e) => addDocumentNameClickHandlerInXmlPath(e)}>Document Name without Extension</Dropdown.Item>
                        <Dropdown.Item style={{ fontSize: "80%" }} onClick={(e) => addDocumentExtensionClickHandlerInXmlPath(e)}>Document Extension</Dropdown.Item>
                        <Dropdown.Item style={{ fontSize: "80%" }} onClick={(e) => addCreatedDateClickHandlerInXmlPath(e)}>Created Date</Dropdown.Item>
                      </Dropdown.Menu>
                    </Dropdown>
                  </div>
                  <CodeEditor
                    id="xmlPath-editor"
                    value={form.xmlPath}
                    language="js"
                    placeholder="Please enter XML path"
                    onChange={(e) => xmlPathChangeHandler(e)}
                    onFocus={() => setXmlPathSelectionStart(0)}
                    padding={15}
                    style={{
                      border: "1px solid #333",
                    }}
                  />
                </Form.Group>
                <Form.Group className="col-12" controlId="addForm.sourceName">
                  <Form.Label>XML Editor</Form.Label>
                  <div style={{ border: "1px solid #000", display: "flex" }}>
                    <Dropdown style={{ display: "flex", flexDirection: "row"}}>
                      <Dropdown.Toggle id="dropdown" style={{ fontSize: "80%", borderRadius: 0, borderRight: "1px solid #fff" }}>
                        Add Parsed Results
                      </Dropdown.Toggle>
                      <Dropdown.Menu style={{ borderRadius: 0, padding: 0 }}>
                        {rules.map(rule => (
                          <Dropdown.Item key={rule.id} style={{ fontSize: "80%" }} onClick={(e) => addParsedResultClickHandlerInTemplate(e, rule)}>{rule.name}</Dropdown.Item>
                        ))}
                      </Dropdown.Menu>
                    </Dropdown>
                    <Dropdown>
                      <Dropdown.Toggle id="dropdown" style={{ fontSize: "80%", borderRadius: 0 }}>
                        Add Document Properties
                      </Dropdown.Toggle>
                      <Dropdown.Menu style={{ borderRadius: 0, padding: 0 }}>
                        <Dropdown.Item style={{ fontSize: "80%" }} onClick={(e) => addDocumentNameClickHandlerInTemplate(e)}>Document Name without Extension</Dropdown.Item>
                        <Dropdown.Item style={{ fontSize: "80%" }} onClick={(e) => addDocumentExtensionClickHandlerInTemplate(e)}>Document Extension</Dropdown.Item>
                        <Dropdown.Item style={{ fontSize: "80%" }} onClick={(e) => addCreatedDateClickHandlerInTemplate(e)}>Created Date</Dropdown.Item>
                      </Dropdown.Menu>
                    </Dropdown>
                  </div>
                  <CodeEditor
                    id="template-editor"
                    value={form.template}
                    language="js"
                    placeholder="Please enter template"
                    onChange={(e) => templateChangeHandler(e)}
                    onFocus={() => setTemplateSelectionStart(0)}
                    padding={15}
                    style={{
                      border: "1px solid #333",
                    }}
                  />
                  </Form.Group>*/}
                <IntegrationEdtior 
                  editorId="xmlPath"
                  displayName="XML Path Editor" 
                  rules={rules}
                  value={form.xmlPath}
                  placeholder="Please enter XML path"
                  onChange={xmlPathChangeHandler}/>
                <IntegrationEdtior 
                  editorId="xmlTemplate"
                  displayName="XML Template Editor" 
                  rules={rules}
                  value={form.template}
                  placeholder="Please enter PDF path"
                  onChange={templateChangeHandler}/>
                <Form.Group
                  className="col-12"
                  controlId="addForm.intervalSeconds"
                >
                  <Form.Label>Interval Seconds</Form.Label>
                  <Form.Control
                    type="number"
                    placeholder="Interval Seconds"
                    value={form.intervalSeconds}
                    onChange={(e) => {
                      setForm(
                        produce((draft) => {
                          draft.intervalSeconds = e.target.value;
                        })
                      );
                    }}
                  />
                </Form.Group>
                <Form.Group className="col-12" controlId="addForm.activated">
                  <Form.Check
                    type="checkbox"
                    placeholder="Activated"
                    label="Activated"
                    checked={form.activated}
                    onChange={(e) => {
                      setForm(
                        produce((draft) => {
                          draft.activated = e.target.checked;
                        })
                      );
                    }}
                  />
                </Form.Group>
                {form.errorMessage && (
                  <p class="errorMessage">{form.errorMessage}</p>
                )}
                {props.type == "add" && (
                  <Button
                    onClick={addBtnClickHandler}
                    style={{ marginRight: 10 }}
                  >
                    Add XML Integration
                  </Button>
                )}
                {props.type == "edit" && (
                  <Button
                    onClick={saveBtnClickHandler}
                    style={{ marginRight: 10 }}
                  >
                    Save
                  </Button>
                )}
                <Button variant="secondary" onClick={backBtnClickHandler}>
                  Back
                </Button>
              </Form>
            </Accordion.Body>
          </Accordion.Item>
        </Accordion>
      </div>
    </WorkspaceLayout>
  );
}
