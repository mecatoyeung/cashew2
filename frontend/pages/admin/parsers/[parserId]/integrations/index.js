import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { produce } from 'immer'

import { Form } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Button } from 'react-bootstrap'
import { Dropdown, DropdownButton } from 'react-bootstrap'

import Select from 'react-select'

import { AgGridReact } from 'ag-grid-react'

import AdminLayout from '../../../../../layouts/admin'

import service from '../../../../../service'

import integrationsStyles from '../../../../../styles/Integrations.module.css'

export default function Parsers() {
  const router = useRouter()

  const { parserId } = router.query

  const gridRef = useRef()
  const [rowData, setRowData] = useState([])
  const [columnDefs, setColumnDefs] = useState([
    { field: 'id', resizable: true },
    { field: 'name', resizable: true, filter: true },
    {
      field: 'actions',
      resizable: true,
      width: 170,
      cellRenderer: (params) => {
        let integration = params.data
        if (integration == undefined) {
          return
        }
        return (
          <div style={{ display: 'flex', flexDirection: 'row' }}>
            <Button
              variant="primary"
              onClick={() => modifyBtnClickHandler(integration)}
              style={{ height: 38, marginRight: 10 }}
            >
              Modify
            </Button>
            <Button
              variant="danger"
              onClick={() => deleteBtnClickHandler(integration)}
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

  const getIntegrations = () => {
    if (!parserId) return
    service.get(`parsers/${parserId}/integrations/`, (response) => {
      setRowData(response.data)
    })
  }

  const addXMLIntegrationBtnClickHandler = () => {
    router.push('/admin/parsers/' + parserId + '/integrations/addXML/')
  }

  const addPDFIntegrationBtnClickHandler = () => {
    router.push('/admin/parsers/' + parserId + '/integrations/addPDF/')
  }

  const modifyBtnClickHandler = (integration) => {
    router.push(
      '/admin/parsers/' + parserId + '/integrations/' + integration.id + '/'
    )
  }

  const deleteBtnClickHandler = async (integration) => {
    await service.delete('integrations/' + integration.id + '/')
    getIntegrations()
  }

  useEffect(() => {
    if (!router.isReady) return
  }, [router.isReady])

  useEffect(() => {
    getIntegrations()
  }, [parserId])

  return (
    <>
      {parserId && rowData && (
        <AdminLayout>
          <div className={integrationsStyles.wrapper}>
            <h1 className={integrationsStyles.h1}>Integrations</h1>
            <div className={integrationsStyles.actionsDiv}>
              <DropdownButton
                title="Perform Action"
                className={integrationsStyles.performActionDropdown}
              >
                <Dropdown.Item
                  href="#"
                  onClick={addXMLIntegrationBtnClickHandler}
                >
                  Add XML Integration
                </Dropdown.Item>
                <Dropdown.Item
                  href="#"
                  onClick={addPDFIntegrationBtnClickHandler}
                >
                  Add PDF Integration
                </Dropdown.Item>
              </DropdownButton>
            </div>
            <div
              className={integrationsStyles.agGridDiv + ' ag-theme-alpine'}
              style={{ width: '100%', height: '100%', marginTop: 20 }}
            >
              <AgGridReact
                ref={gridRef}
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
        </AdminLayout>
      )}
    </>
  )
}
