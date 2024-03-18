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

import AdminLayout from '../../../../../../layouts/admin'

import service from '../../../../../../service'

import preProcessingsStyles from "../../../../../../styles/PreProcessings.module.css"

export default function PostProcessingForm(props) {

  const router = useRouter()

  const { parserId, postprocessingId } = router.query

  const [form, setForm] = useState({
    name: "",
    postProcessingType: "REDACTION",
    redactionRegex: "",
    step: 10,
    errorMessage: ""
  })

  const addRedactionBtnClickHandler = () => {
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
    service.post("/postprocessings/", {
      parser: parserId,
      postProcessingType: "REDACTION",
      redactionRegex: form.redactionRegex,
      name: form.name,
      step: form.step
    }, (response) => {
      router.push("/admin/parsers/" + parserId + "/postprocessings/")
    })
  }

  const backBtnClickHandler = () => {
    router.push("/admin/parsers/" + parserId + "/postprocessings/")
  }

  const saveBtnClickHandler = () => {
    service.put("/postprocessings/" + postprocessingId + "/", {
      parser: parserId,
      postProcessingType: form.postProcessingType,
      redactionRegex: form.redactionRegex,
      name: form.name,
      step: form.step
    }, (response) => {
      router.push("/admin/parsers/" + parserId + "/postprocessings/")
    })
  }

  const getPostProcessing = () => {
    if (!postprocessingId) return
    service.get("/postprocessings/" + postprocessingId + "/", (response) => {
      setForm(response.data)
    })
  }

  useEffect(() => {
    if (props.type == "edit") {
      getPostProcessing()
    }
  }, [parserId])

  return (
    <AdminLayout>
      <div className={preProcessingsStyles.wrapper}>
        {props.type == "add" && (
          <h1 className={preProcessingsStyles.h1}>Add Redaction</h1>
        )}
        {props.type == "edit" && (
          <h1 className={preProcessingsStyles.h1}>Edit Redaction</h1>
        )}
        <Accordion defaultActiveKey="0" style={{padding: 10}}>
          <Accordion.Item eventKey="0">
            <Accordion.Header>Please fill in the form</Accordion.Header>
            <Accordion.Body>
              <Form>
                <Form.Group className="col-12" controlId="addForm.name">
                  <Form.Label>Name</Form.Label>
                  <Form.Control type="text" placeholder="Name" value={form.name} onChange={(e) => {
                    setForm(
                      produce((draft) => {
                        draft.name = e.target.value
                      })
                    )
                  }}/>
                </Form.Group>
                <Form.Group className="col-12" controlId="addForm.redactionRegex">
                  <Form.Label>Redaction Regex</Form.Label>
                  <Form.Control type="text" placeholder="For example, dollar amount, ([0-9,]*[.][0-9]{2})" value={form.redactionRegex} onChange={(e) => {
                    setForm(
                      produce((draft) => {
                        draft.redactionRegex = e.target.value
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
                  <Button onClick={addRedactionBtnClickHandler} style={{marginRight: 10}}>Add Redaction</Button>
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
    </AdminLayout>
  )
}
