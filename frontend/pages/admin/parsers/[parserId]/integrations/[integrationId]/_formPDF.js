import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useRouter } from 'next/router'

import { produce } from 'immer'

import { Form } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Button } from 'react-bootstrap'
import { Dropdown } from 'react-bootstrap'
import { Accordion } from 'react-bootstrap'

import Select from 'react-select'

import { AgGridReact } from 'ag-grid-react'

import IntegrationEdtior from '../../../../../../components/integrationEditor'

import WorkspaceLayout from '../../../../../../layouts/admin'

import service from '../../../../../../service'

import rulesStyles from '../../../../../../styles/Sources.module.css'

export default function Parsers(props) {
  const router = useRouter()

  const { parserId, integrationId } = router.query

  const [rules, setRules] = useState(null)

  const [pdfPathSelectionStart, setPdfPathSelectionStart] = useState(0)

  const getRules = () => {
    if (!parserId) return
    service.get(`rules/?parserId=${parserId}`, (response) => {
      setRules(response.data)
    })
  }

  let pdfIntegrationTypeOptions = [
    {
      label: 'Source',
      value: 'SOURCE',
    },
    {
      label: 'Pre Processing',
      value: 'PRE_PROCESSING',
    },
    {
      label: 'OCR',
      value: 'OCR',
    },
    {
      label: 'Post Processing',
      value: 'POST_PROCESSING',
    },
  ]

  const [form, setForm] = useState({
    name: '',
    parser: parserId,
    integrationType: 'PDF_INTEGRATION',
    pdfIntegrationType: 'SOURCE',
    preProcessing: null,
    postProcessing: null,
    pdfPath: '',
    intervalSeconds: 15,
    activated: true,
    errorMessage: '',
  })

  const [preProcessings, setPreProcessings] = useState([])
  const [postProcessings, setPostProcessings] = useState([])

  const selectPdfIntegrationTypeChangeHandler = (e) => {
    setForm(
      produce((draft) => {
        draft.pdfIntegrationType = e.value
      })
    )
  }

  const selectPreProcessingChangeHandler = (e) => {
    setForm(
      produce((draft) => {
        draft.preProcessing = e.value
      })
    )
  }

  const selectPostProcessingChangeHandler = (e) => {
    setForm(
      produce((draft) => {
        draft.postProcessing = e.value
      })
    )
  }

  const addBtnClickHandler = () => {
    let errorMessage = ''
    if (form.name.trim() == '') {
      errorMessage = 'Integration Name should not be empty.'
    }
    if (form.pdfPath.trim() == '') {
      errorMessage = 'PDF Path should not be empty.'
    }
    setForm(
      produce((draft) => {
        draft.errorMessage = errorMessage
      })
    )
    if (errorMessage) {
      return
    }
    service.post(
      '/integrations/',
      {
        name: form.name,
        parser: parserId,
        integrationType: form.integrationType,
        pdfIntegrationType: form.pdfIntegrationType,
        preProcessing: form.preProcessing,
        postProcessing: form.postProcessing,
        pdfPath: form.pdfPath,
        intervalSeconds: form.intervalSeconds,
        activated: form.activated,
      },
      (response) => {
        router.push('/admin/parsers/' + parserId + '/integrations/')
      }
    )
  }

  const backBtnClickHandler = () => {
    router.push('/admin/parsers/' + parserId + '/integrations/')
  }

  const saveBtnClickHandler = () => {
    service.put(
      '/integrations/' + integrationId + '/',
      {
        name: form.name,
        parser: parserId,
        integrationType: form.integrationType,
        pdfIntegrationType: form.pdfIntegrationType,
        preProcessing: form.preProcessing,
        postProcessing: form.postProcessing,
        pdfPath: form.pdfPath,
        intervalSeconds: form.intervalSeconds,
        activated: form.activated,
      },
      (response) => {
        router.push('/admin/parsers/' + parserId + '/integrations/')
      }
    )
  }

  const getIntegration = () => {
    if (!integrationId) return
    service.get('/integrations/' + integrationId + '/', (response) => {
      setForm(
        produce((draft) => {
          draft.name = response.data.name
          draft.parser = parserId
          draft.integrationType = response.data.integrationType
          draft.pdfIntegrationType = response.data.pdfIntegrationType
          draft.preProcessing = response.data.preProcessing
          draft.postProcessing = response.data.postProcessing
          draft.pdfPath = response.data.pdfPath
          draft.intervalSeconds = response.data.intervalSeconds
          draft.activated = response.data.activated
        })
      )
    })
  }

  const getPreProcessings = () => {
    if (!parserId) return
    service.get('/preprocessings?parserId=' + parserId, (response) => {
      setPreProcessings(response.data)
    })
  }

  const getPostProcessings = () => {
    if (!parserId) return
    service.get('/postprocessings?parserId=' + parserId, (response) => {
      setPostProcessings(response.data)
    })
  }

  const pdfPathChangeHandler = (e) => {
    setPdfPathSelectionStart(0)
    e.target.value = e.target.value.replace(/[\r\n]+/g, ' ')
    setForm(
      produce((draft) => {
        draft.pdfPath = e.target.value
      })
    )
  }

  useEffect(() => {
    if (props.type == 'edit') {
      getIntegration()
    }
    getPreProcessings()
    getPostProcessings()
    getRules()
  }, [parserId, integrationId])

  return (
    <WorkspaceLayout>
      <div className={rulesStyles.wrapper}>
        {props.type == 'add' && (
          <h1 className={rulesStyles.h1}>Add PDF Integration</h1>
        )}
        {props.type == 'edit' && (
          <h1 className={rulesStyles.h1}>Edit PDF Integration</h1>
        )}
        <Accordion defaultActiveKey="0" style={{ padding: 10 }}>
          <Accordion.Item eventKey="0">
            <Accordion.Header>Please fill in the form</Accordion.Header>
            <Accordion.Body>
              <Form>
                <Form.Group className="col-12" controlId="addForm.sourceName">
                  <Form.Label>Integration Name</Form.Label>
                  <Form.Control
                    type="name"
                    placeholder="Integration Name"
                    value={form.name}
                    onChange={(e) => {
                      setForm(
                        produce((draft) => {
                          draft.name = e.target.value
                        })
                      )
                    }}
                  />
                </Form.Group>
                <Form.Group
                  className="col-12"
                  controlId="addForm.pdfIntegrationType"
                >
                  <Form.Label>PDF Integration Type</Form.Label>
                  <Select
                    classNamePrefix="react-select"
                    options={pdfIntegrationTypeOptions}
                    value={pdfIntegrationTypeOptions.find(
                      (o) => o.value == form.pdfIntegrationType
                    )}
                    onChange={(e) => selectPdfIntegrationTypeChangeHandler(e)}
                    menuPlacement="auto"
                    menuPosition="fixed"
                  />
                </Form.Group>
                {form.pdfIntegrationType == 'PRE_PROCESSING' &&
                  preProcessings && (
                    <Form.Group
                      className="col-12"
                      controlId="addForm.preProcessingId"
                    >
                      <Form.Label>Pre-processing</Form.Label>
                      <Select
                        classNamePrefix="react-select"
                        options={preProcessings.map((pp) => {
                          return {
                            label: pp.name,
                            value: pp.id,
                          }
                        })}
                        value={preProcessings
                          .map((pp) => {
                            return {
                              label: pp.name,
                              value: pp.id,
                            }
                          })
                          .find((o) => o.value == form.preProcessing)}
                        onChange={(e) => selectPreProcessingChangeHandler(e)}
                        menuPlacement="auto"
                        menuPosition="fixed"
                      />
                    </Form.Group>
                  )}
                {form.pdfIntegrationType == 'POST_PROCESSING' &&
                  postProcessings && (
                    <Form.Group
                      className="col-12"
                      controlId="addForm.postProcessingId"
                    >
                      <Form.Label>Post-processing</Form.Label>
                      <Select
                        classNamePrefix="react-select"
                        options={postProcessings.map((pp) => {
                          return {
                            label: pp.name,
                            value: pp.id,
                          }
                        })}
                        value={postProcessings
                          .map((pp) => {
                            return {
                              label: pp.name,
                              value: pp.id,
                            }
                          })
                          .find((o) => o.value == form.postProcessing)}
                        onChange={selectPostProcessingChangeHandler}
                        menuPlacement="auto"
                        menuPosition="fixed"
                      />
                    </Form.Group>
                  )}
                {rules && (
                  <IntegrationEdtior
                    editorId="pdfPath"
                    displayName="PDF Output Path"
                    rules={rules}
                    value={form.pdfPath}
                    placeholder="Please enter PDF path"
                    onChange={pdfPathChangeHandler}
                  />
                )}
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
                          draft.intervalSeconds = e.target.value
                        })
                      )
                    }}
                  />
                </Form.Group>
                <Form.Group className="col-12" controlId="addForm.activated">
                  <Form.Check
                    type="checkbox"
                    placeholder="Activated"
                    label="activated"
                    checked={form.activated}
                    onChange={(e) => {
                      setForm(
                        produce((draft) => {
                          draft.activated = e.target.checked
                        })
                      )
                    }}
                  />
                </Form.Group>
                {form.errorMessage && (
                  <p class="errorMessage">{form.errorMessage}</p>
                )}
                {props.type == 'add' && (
                  <Button
                    onClick={addBtnClickHandler}
                    style={{ marginRight: 10 }}
                  >
                    Add PDF Integration
                  </Button>
                )}
                {props.type == 'edit' && (
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
  )
}
