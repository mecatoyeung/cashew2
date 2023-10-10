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

import WorkspaceLayout from '../../../../../layouts/workspace'

import service from '../../../../../service'

import rulesStyles from "../../../../../styles/Sources.module.css"

export default function Parsers(props) {

  const router = useRouter()

  const { parserId, sourceId } = router.query

  const [form, setForm] = useState({
    name: "",
    sourcePath: "",
    intervalSeconds: 15,
    activated: false,
    errorMessage: ""
  })

  const addSourceBtnClickHandler = () => {
    let errorMessage = ""
    if (form.name.trim() == "") {
      errorMessage = "Source name should not be empty."
    }
    if (form.sourcePath.trim() == "") {
      errorMessage = "Source path should not be empty."
    }
    setForm(
      produce((draft) => {
        draft.errorMessage = errorMessage
      })
    )
    if (errorMessage) {
      return
    }
    service.post("/sources/", {
      parser: parserId,
      name: form.name,
      sourcePath: form.sourcePath,
      intervalSeconds: form.intervalSeconds,
      activated: form.activated
    }, (response) => {
      router.push("/workspace/parsers/" + parserId + "/sources/")
    })
  }

  const backBtnClickHandler = () => {
    router.push("/workspace/parsers/" + parserId + "/sources/")
  }

  const saveBtnClickHandler = () => {
    service.put("/sources/" + sourceId + "/", {
      parser: parserId,
      name: form.name,
      sourcePath: form.sourcePath,
      intervalSeconds: form.intervalSeconds,
      activated: form.activated
    }, (response) => {
      router.push("/workspace/parsers/" + parserId + "/sources/")
    })
  }

  useEffect(() => {
    if (props.type == "edit") {
      service.get("/sources/" + sourceId + "/", (response) => {
        setForm(produce((draft) => {
          draft.name = response.data.name
          draft.sourcePath = response.data.sourcePath
          draft.intervalSeconds = response.data.intervalSeconds
          draft.activated = response.data.activated
        }))
      })
    }
  }, [parserId])

  return (
    <WorkspaceLayout>
      <div className={rulesStyles.wrapper}>
        <h1 className={rulesStyles.h1}>Add Source</h1>
        <Accordion defaultActiveKey="0" style={{padding: 10}}>
          <Accordion.Item eventKey="0">
            <Accordion.Header>Please fill in the form</Accordion.Header>
            <Accordion.Body>
              <Form>
                <Form.Group className="col-12" controlId="addForm.sourceName">
                  <Form.Label>Source Name</Form.Label>
                  <Form.Control type="name" placeholder="File Source" value={form.name} onChange={(e) => {
                    setForm(
                      produce((draft) => {
                        draft.name = e.target.value
                      })
                    )
                  }}/>
                </Form.Group>
                <Form.Group className="col-12" controlId="addForm.sourcePath">
                  <Form.Label>Source Path</Form.Label>
                  <Form.Control type="name" placeholder="Source Path" value={form.sourcePath} onChange={(e) => {
                    setForm(
                      produce((draft) => {
                        draft.sourcePath = e.target.value
                      })
                    )
                  }}/>
                </Form.Group>
                <Form.Group className="col-12" controlId="addForm.intervalSeconds">
                  <Form.Label>Interval Seconds</Form.Label>
                  <Form.Control type="number" placeholder="Interval Seconds"  value={form.intervalSeconds} onChange={(e) => {
                    setForm(
                      produce((draft) => {
                        draft.intervalSeconds = e.target.value
                      })
                    )
                  }}/>
                </Form.Group>
                <Form.Group className="col-12" controlId="addForm.activated">
                  <Form.Check type="checkbox" placeholder="Activated" label="activated" checked={form.activated} onChange={(e) => {
                    setForm(
                      produce((draft) => {
                        draft.activated = e.target.checked
                      })
                    )
                  }}/>
                </Form.Group>
                {form.errorMessage && (
                  <p class="errorMessage">{form.errorMessage}</p>
                )}
                {props.type == "add" && (
                  <Button onClick={addSourceBtnClickHandler} style={{marginRight: 10}}>Add Source</Button>
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
