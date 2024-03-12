import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { produce } from 'immer'

import { Form } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Button } from 'react-bootstrap'
import { Dropdown } from 'react-bootstrap'
import { Accordion } from 'react-bootstrap';

import Select from 'react-select'

import { AgGridReact } from 'ag-grid-react'

import WorkspaceLayout from '../../../../../../layouts/workspace'

import service from '../../../../../../service'

import preProcessingsStyles from "../../../../../../styles/PreProcessings.module.css"

const orientationDetectionTypeOptions = [
  {
    label: "Orientation Detection (DocTR)",
    value: "ORIENTATION_DETECTION_DOCTR"
  }
]

export default function PreProcessingForm(props) {

  const router = useRouter()

  const { parserId, preprocessingId } = router.query

  const [form, setForm] = useState({
    name: "",
    preProcessingType: "ORIENTATION_DETECTION_DOCTR",
    orientationDetectionTesseractConfidenceAbove: 0.5,
    step: 10,
    debug: false,
    errorMessage: ""
  })

  const addOrientationDetectionBtnClickHandler = () => {
    let errorMessage = ""
    if (form.name.trim() == "") {
      errorMessage = "Source name should not be empty."
    }
    setForm(
      produce((draft) => {
        draft.errorMessage = errorMessage
      })
    )
    if (errorMessage) {
      return
    }
    service.post("/preprocessings/", {
      name: form.name,
      parser: parserId,
      preProcessingType: form.preProcessingType,
      orientationDetectionTesseractConfidenceAbove: form.orientationDetectionTesseractConfidenceAbove,
      debug: form.debug,
      step: form.step
    }, (response) => {
      router.push("/workspace/parsers/" + parserId + "/preprocessings/")
    })
  }

  const backBtnClickHandler = () => {
    router.push("/workspace/parsers/" + parserId + "/preprocessings/")
  }

  const saveBtnClickHandler = () => {
    service.put("/preprocessings/" + preprocessingId + "/", {
      name: form.name,
      parser: parserId,
      preProcessingType: form.preProcessingType,
      orientationDetectionTesseractConfidenceAbove: form.orientationDetectionTesseractConfidenceAbove,
      debug: form.debug,
      step: form.step
    }, (response) => {
      router.push("/workspace/parsers/" + parserId + "/preprocessings/")
    })
  }

  const getPreProcessing = () => {
    if (!preprocessingId) return
    service.get("/preprocessings/" + preprocessingId + "/", (response) => {
      setForm(produce((draft) => {
        draft.name = response.data.name
        draft.preProcessingType = response.data.preProcessingType,
        draft.orientationDetectionTesseractConfidenceAbove = response.data.orientationDetectionTesseractConfidenceAbove
        draft.debug = response.data.debug
        draft.step = response.data.step
      }))
    })
  }

  const selectOrientationDetectionTypeChangeHandler = (e) => {
    setForm(produce((draft) => {
      draft.preProcessingType = e.value
    }))
  }

  useEffect(() => {
    if (props.type == "edit") {
      getPreProcessing()
    }
  }, [parserId])

  return (
    <WorkspaceLayout>
      <div className={preProcessingsStyles.wrapper}>
        <h1 className={preProcessingsStyles.h1}>Add Orientation Detection</h1>
        <Accordion defaultActiveKey="0" style={{padding: 10}}>
          <Accordion.Item eventKey="0">
            <Accordion.Header>Please fill in the form</Accordion.Header>
            <Accordion.Body>
              <Form>
                <Form.Group className="col-12" controlId="addForm.name">
                  <Form.Label>Name</Form.Label>
                  <Form.Control type="name" placeholder="Name" value={form.name} onChange={(e) => {
                    setForm(
                      produce((draft) => {
                        draft.name = e.target.value
                      })
                    )
                  }}/>
                </Form.Group>
                <Form.Group className="col-12" controlId="addForm.orientationDetectionType">
                  <Form.Label>Orientation Detection Type</Form.Label>
                  <Select
                    classNamePrefix="react-select"
                    options={orientationDetectionTypeOptions}
                    value={orientationDetectionTypeOptions.find(o => o.value == form.preProcessingType)}
                    onChange={(e) => selectOrientationDetectionTypeChangeHandler(e)}
                    menuPlacement="auto"
                    menuPosition="fixed" />
                </Form.Group>
                {form.preProcessingType == "ORIENTATION_DETECTION_TESSERACT" && (
                  <Form.Group className="col-12" controlId="addForm.orientationDetectionTesseractConfidenceAbove" style={{marginBottom: 10 }}>
                    <Form.Label>Confidence above this value would take effect</Form.Label>
                    <Form.Control type="number" placeholder="(Default: 0.5)" value={form.orientationDetectionTesseractConfidenceAbove} onChange={(e) => {
                      setForm(
                        produce((draft) => {
                          draft.orientationDetectionTesseractConfidenceAbove = e.target.value
                        })
                      )
                    }}/>
                  </Form.Group>
                )}
                {form.preProcessingType == "ORIENTATION_DETECTION_OPENCV" && (
                  <Form.Group className="col-12" controlId="addForm.debug">
                    <Form.Check type="checkbox" placeholder="Debug" label="Debug" checked={form.debug} onChange={(e) => {
                      setForm(
                        produce((draft) => {
                          draft.debug = e.target.checked
                        })
                      )
                    }}/>
                  </Form.Group>
                )}
                <Form.Group className="col-12" controlId="addForm.step" style={{marginBottom: 10 }}>
                  <Form.Label>Sort Order (from smallest to largest)</Form.Label>
                  <Form.Control type="number" placeholder="(from smallest to largest)" value={form.step} onChange={(e) => {
                    setForm(
                      produce((draft) => {
                        draft.step = e.target.value
                      })
                    )
                  }}/>
                </Form.Group>
                {form.errorMessage && (
                  <p class="errorMessage">{form.errorMessage}</p>
                )}
                {props.type == "add" && (
                  <Button onClick={addOrientationDetectionBtnClickHandler} style={{marginRight: 10}}>Add Orientation Detection</Button>
                )}
                {props.type == "edit" && (
                  <Button onClick={saveBtnClickHandler} style={{marginRight: 10}}>Save</Button>
                )}
                <Button variant='secondary' onClick={backBtnClickHandler}>Back</Button>
              </Form>
            </Accordion.Body>
          </Accordion.Item>
        </Accordion>
      </div>
    </WorkspaceLayout>
  )
}
