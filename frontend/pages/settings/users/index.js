import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { AgGridReact } from 'ag-grid-react'

import { produce } from 'immer'

import { Form } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Button } from 'react-bootstrap'
import { Dropdown } from 'react-bootstrap'
import { Row, Col } from 'react-bootstrap'

import Select from 'react-select'

import SettingsLayout from '../../../layouts/settings'

import service from '../../../service'

import accountStyles from '../../../styles/Account.module.css'

export default function Users() {
  const router = useRouter()

  const { parserId } = router.query

  const gridRef = useRef()
  const [rowData, setRowData] = useState([])
  const [columnDefs, setColumnDefs] = useState([
    { header: 'Id', field: 'id', resizable: true },
    {
      header: 'Display Name',
      field: 'displayName',
      resizable: true,
      filter: true,
      cellRenderer: (params) => {
        let user = params.data
        return user.profile.fullName
      },
    },
    { header: 'Username', field: 'username', resizable: true, filter: true },
    { header: 'Email', field: 'email', resizable: true, filter: true },
    { header: 'Is Active', field: 'isActive', resizable: true, filter: true },
    {
      header: 'actions',
      field: 'actions',
      resizable: true,
      width: 300,
      cellRenderer: (params) => {
        let user = params.data
        return (
          <div style={{ display: 'flex', flexDirection: 'row' }}>
            <Button
              variant="primary"
              onClick={() => {
                editUserBtnClickHandler(user)
              }}
              style={{ height: 38, marginRight: 10 }}
            >
              Edit
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

  const editUserBtnClickHandler = (user) => {
    router.push('/settings/users/' + user.id + '/')
  }

  const getUsers = () => {
    service.get(`users/`, (response) => {
      setRowData(response.data)
    })
  }

  useEffect(() => {
    getUsers()
  }, [router.isReady, parserId])

  return (
    <SettingsLayout>
      <h1 className={accountStyles.h1}>Users</h1>
      <div className={accountStyles.usersDiv}>
        <Form>
          <Row>
            <Col style={{ paddingLeft: 10, paddingRight: 10 }}>
              <Button onClick={() => router.push('/settings/users/add')}>
                Add User
              </Button>
            </Col>
          </Row>
          <Row>
            <div
              className={accountStyles.agGridDiv + ' ag-theme-alpine'}
              style={{ width: '100%', height: '640px', marginTop: 20 }}
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
          </Row>
        </Form>
      </div>
    </SettingsLayout>
  )
}
