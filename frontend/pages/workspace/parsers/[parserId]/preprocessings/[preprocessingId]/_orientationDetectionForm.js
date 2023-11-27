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

export default function PreProcessingForm(props) {

  const router = useRouter()

  const { parserId, preprocessingId } = router.query

  const [form, setForm] = useState({
    name: "",
    preProcessingType: "ORIENTATION_DETECTION",
    step: 10,
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
      parser: parserId,
      preProcessingType: "ORIENTATION_DETECTION",
      name: form.name,
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
      parser: parserId,
      preProcessingType: form.preProcessingType,
      name: form.name,
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
        draft.preProcessingType = form.preProcessingType,
        draft.step = response.data.step
      }))
    })
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