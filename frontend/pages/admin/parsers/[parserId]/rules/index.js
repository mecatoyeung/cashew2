import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useRouter } from 'next/router'
import { useParams } from 'next/navigation'
import Image from 'next/image'

import { produce } from 'immer'

import { Form } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Button } from 'react-bootstrap'
import { Dropdown } from 'react-bootstrap'

import Select from 'react-select'

import { AgGridReact } from 'ag-grid-react'

import WorkspaceLayout from '../../../../../layouts/admin'

import service from '../../../../../service'

import rulesStyles from '../../../../../styles/Rules.module.css'

export default function Parsers() {
  const router = useRouter()

  const { parserId } = router.query

  const ruleTypes = [
    { label: 'Textfield', value: 'TEXTFIELD' },
    { label: 'Anchored Textfield', value: 'ANCHORED_TEXTFIELD' },
    { label: 'Table', value: 'TABLE' },
    { label: 'Acrobat Form', value: 'ACROBAT_FORM' },
    { label: 'Barcode', value: 'BARCODE' },
    { label: 'Input Textfield (In Progress)', value: 'INPUT_TEXTFIELD' },
    { label: 'Input Dropdown (In Progress)', value: 'INPUT_DROPDOWN' },
    { label: 'Dependent Rule', value: 'DEPENDENT_RULE' },
  ]

  const gridRef = useRef()
  const [rules, setRules] = useState([])
  const [rowData, setRowData] = useState([])
  const [columnDefs, setColumnDefs] = useState([
    { field: 'id', resizable: true },
    { field: 'name', resizable: true, filter: true },
    {
      field: 'actions',
      resizable: true,
      width: 170,
      cellRenderer: (params) => {
        let rule = params.data
        return (
          <div style={{ display: 'flex', flexDirection: 'row' }}>
            <Dropdown
              style={{
                display: 'inline-block',
                verticalAlign: 'top',
                lineHeight: 'initial',
                overflow: 'visible',
              }}
            >
              <Dropdown.Toggle
                variant="primary"
                id={'dropdown-edit-' + rule.id}
              >
                Edit
              </Dropdown.Toggle>
              <Dropdown.Menu>
                <Dropdown.Item onClick={() => rulePropertiesClickHandler(rule)}>
                  Rule Properties
                </Dropdown.Item>
                {(rule.ruleType == 'TEXTFIELD' ||
                  rule.ruleType == 'ANCHORED_TEXTFIELD' ||
                  rule.ruleType == 'TABLE' ||
                  rule.ruleType == 'BARCODE') && (
                  <>
                    <Dropdown.Item
                      onClick={() => regionSelectorClickHandler(rule)}
                    >
                      Region Selector
                    </Dropdown.Item>
                  </>
                )}
                {rule.ruleType == 'ACROBAT_FORM' && (
                  <>
                    <Dropdown.Item
                      onClick={() => acrobatFormFieldSelectorClickHandler(rule)}
                    >
                      Field Selector
                    </Dropdown.Item>
                  </>
                )}
                <Dropdown.Item onClick={() => streamEditorClickHandler(rule)}>
                  Stream Editor
                </Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
            &nbsp;
            <Button
              variant="danger"
              onClick={() => deleteBtnClickHandler(rule)}
              style={{ height: 38 }}
            >
              Delete
            </Button>
          </div>
        )
      },
    },
  ])
  const defaultColDef = useMemo(
    () => ({
      sortable: true,
    }),
    []
  )
  const cellClickedListener = useCallback((event) => {}, [])

  const [addRuleForm, setAddRuleForm] = useState({
    show: false,
    name: '',
    type: '',
    dependsOn: 0,
  })

  const getRules = () => {
    if (!parserId) return
    service.get(`rules/?parserId=${parserId}`, (response) => {
      setRules(
        response.data
          .filter((r) => r.ruleType != 'DEPENDENT_RULE')
          .map((r) => {
            return {
              value: r.id,
              label: r.name,
            }
          })
      )
      setRowData(response.data)
    })
  }

  const addRuleBtnClickHandler = () => {
    setAddRuleForm(
      produce((draft) => {
        draft.show = true
      })
    )
  }

  const rulePropertiesClickHandler = (rule) => {
    router.push(
      '/admin/parsers/' +
        parserId +
        '/rules/' +
        rule.id +
        '?type=ruleProperties'
    )
  }

  const regionSelectorClickHandler = (rule) => {
    router.push(
      '/admin/parsers/' +
        parserId +
        '/rules/' +
        rule.id +
        '?type=regionSelector'
    )
  }

  const streamEditorClickHandler = (rule) => {
    router.push(
      '/admin/parsers/' + parserId + '/rules/' + rule.id + '/?type=streamEditor'
    )
  }

  const acrobatFormFieldSelectorClickHandler = (rule) => {
    router.push(
      '/admin/parsers/' +
        parserId +
        '/rules/' +
        rule.id +
        '?type=acrobatFormFieldSelector'
    )
  }

  const deleteBtnClickHandler = (rule) => {
    service.delete('rules/' + rule.id + '/', (response) => {
      getRules()
    })
  }

  const closeRuleBtnClickHandler = () => {
    setAddRuleForm(
      produce((draft) => {
        draft.show = false
      })
    )
  }

  const ruleNameChangeHandler = (e) => {
    setAddRuleForm(
      produce((draft) => {
        draft.name = e.target.value
      })
    )
  }

  const ruleTypeChangeHandler = (e) => {
    setAddRuleForm(
      produce((draft) => {
        draft.type = e.value
      })
    )
  }

  const dependsOnChangeHandler = (e) => {
    setAddRuleForm(
      produce((draft) => {
        draft.dependsOn = e.value
      })
    )
  }

  const confirmAddRuleBtnClickHandler = () => {
    service.post(
      'rules/',
      {
        parser: parserId,
        ruleType: addRuleForm.type,
        name: addRuleForm.name,
        pages: '1',
        x1: 10,
        y1: 10,
        x2: 20,
        y2: 15,
        dependsOn:
          addRuleForm.type == 'DEPENDENT_RULE' ? addRuleForm.dependsOn : null,
      },
      () => {
        getRules()
        setAddRuleForm(
          produce((draft) => {
            draft.show = false
          })
        )
      },
      (error) => {
        console.error(error)
      }
    )
  }

  useEffect(() => {
    if (!router.isReady) return
    if (!router.query.parserId) return
  }, [router.isReady])

  useEffect(() => {
    getRules()
  }, [parserId])

  return (
    <WorkspaceLayout>
      {parserId && (
        <div className={rulesStyles.wrapper}>
          <h1 className={rulesStyles.h1}>Fields</h1>
          <div className={rulesStyles.actionsDiv}>
            <Button
              className={rulesStyles.actionBtn}
              onClick={addRuleBtnClickHandler}
            >
              Add Field
            </Button>
            <Modal
              show={addRuleForm.show}
              onHide={closeRuleBtnClickHandler}
              centered
            >
              <Modal.Header closeButton>
                <Modal.Title>Add Field</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                <Form>
                  <Form.Group className="mb-3" controlId="ruleNameControlInput">
                    <Form.Label>Name</Form.Label>
                    <Form.Control
                      type="text"
                      placeholder="e.g. Document No"
                      value={addRuleForm.name}
                      onChange={ruleNameChangeHandler}
                    />
                  </Form.Group>
                  <Form.Group className="mb-3" controlId="ruleTypeControlInput">
                    <Form.Label>Type</Form.Label>
                    <Select
                      instanceId="ruleTypeSelectId"
                      options={ruleTypes}
                      onChange={ruleTypeChangeHandler}
                      value={ruleTypes.find((t) => t.value == addRuleForm.type)}
                    />
                  </Form.Group>
                  {addRuleForm.type == 'DEPENDENT_RULE' && (
                    <Form.Group
                      className="mb-3"
                      controlId="ruleTypeControlInput"
                    >
                      <Form.Label>Depends on</Form.Label>
                      <Select
                        instanceId="dependsOnSelectId"
                        options={rules}
                        onChange={dependsOnChangeHandler}
                        value={rules.find(
                          (r) => r.value == addRuleForm.dependsOn
                        )}
                      />
                    </Form.Group>
                  )}
                </Form>
              </Modal.Body>
              <Modal.Footer>
                <Button
                  variant="primary"
                  onClick={confirmAddRuleBtnClickHandler}
                >
                  Add
                </Button>
                <Button variant="secondary" onClick={closeRuleBtnClickHandler}>
                  Close
                </Button>
              </Modal.Footer>
            </Modal>
          </div>
          <div
            className={rulesStyles.agGridDiv + ' ag-theme-alpine'}
            style={{ width: '100%', height: '100%', marginTop: 20 }}
          >
            <AgGridReact
              ref={gridRef}
              suppressRowTransform
              rowData={rowData}
              columnDefs={columnDefs}
              defaultColDef={defaultColDef}
              animateRows={true}
              rowSelection="multiple"
              onCellClicked={cellClickedListener}
              onModelUpdated={(params) => {
                params.columnApi.autoSizeColumns(['id'])
              }}
            />
          </div>
        </div>
      )}
    </WorkspaceLayout>
  )
}
