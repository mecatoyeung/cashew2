import Head from 'next/head'
import Image from 'next/image'
import Link from 'next/link'

import { useRouter } from 'next/router'
import { useState, useEffect } from 'react'

import { Nav } from 'react-bootstrap'
import { Button } from 'react-bootstrap'
import Dropdown from 'react-bootstrap/Dropdown'
import DropdownButton from 'react-bootstrap/DropdownButton'

import AdminHeader from './_adminHeader'

import service from '../service'

import hasPermission from '../helpers/hasPermission'

import 'bootstrap-daterangepicker/daterangepicker.css'
import adminStyles from '../styles/AdminLayout.module.css'

export default function WorkspaceLayout({ children }) {
  const router = useRouter()

  let { parserId } = router.query

  const [parser, setParser] = useState(null)
  const [user, setUser] = useState(null)

  const getParser = () => {
    if (!parserId) return
    service.get('parsers/' + parserId + '/', (response) => {
      setParser(response.data)
    })
  }

  const getUserProfile = () => {
    service.get('account/', (response) => {
      setUser(response.data)
    })
  }

  const logoutBtnClickHandler = () => {
    service.post('rest-auth/logout/', {}, () => {
      localStorage.removeItem('token')
      router.push('/')
    })
  }

  const sourcesClickHandler = () => {
    router.push('/admin/parsers/' + parserId + '/sources')
  }

  const queuesClickHandler = () => {
    router.push('/admin/parsers/' + parserId + '/queues')
  }

  const preprocessingsClickHandler = () => {
    router.push('/admin/parsers/' + parserId + '/preprocessings')
  }

  const ocrClickHandler = () => {
    router.push('/admin/parsers/' + parserId + '/ocr')
  }

  const aiChatClickHandler = () => {
    router.push('/admin/parsers/' + parserId + '/aichat')
  }

  const fieldsClickHandler = () => {
    router.push('/admin/parsers/' + parserId + '/rules')
  }

  const splittingClickHandler = () => {
    router.push('/admin/parsers/' + parserId + '/splitting')
  }

  const postprocessingsClickHandler = () => {
    router.push('/admin/parsers/' + parserId + '/postprocessings')
  }

  const integrationsClickHandler = () => {
    router.push('/admin/parsers/' + parserId + '/integrations')
  }

  const statisticsClickHandler = () => {
    router.push('/admin/parsers/' + parserId + '/statistics')
  }

  const settingsClickHandler = () => {
    router.push('/admin/parsers/' + parserId + '/settings')
  }

  useEffect(() => {
    if (!hasPermission('cashew_parser_management')) {
      router.push('/workbench/parsers')
    }
  })

  useEffect(() => {
    getUserProfile()
  }, [])

  useEffect(() => {
    getParser()
  }, [parserId])

  return (
    <>
      <Head>
        <title>Cashew Docparser</title>
        <meta name="description" content="Written by Cato Yeung" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"
        ></meta>
        <link rel="icon" href="/static/favicon.ico" />
      </Head>
      {parser && (
        <div className={adminStyles.wrapper}>
          <AdminHeader />
          <hr className={adminStyles.headerHr} />
          <main className={adminStyles.main + ' d-flex flex-column'}>
            <div
              className={
                adminStyles.sideNavContainerDiv + ' d-flex flex-grow-1'
              }
            >
              <div
                className="row d-flex flex-grow-1"
                style={{ padding: 0, margin: 0, flexDirection: 'row' }}
              >
                <div
                  className="col-12 col-md-2 d-flex"
                  style={{ paddingLeft: 0, paddingRight: 0, width: 200 }}
                >
                  <div
                    className={adminStyles.sideNavDiv + ' d-flex flex-grow-1'}
                  >
                    <ul className={adminStyles.sideNavUl}>
                      {parser && (
                        <li
                          style={{
                            fontFamily: 'Oswald, sans',
                            fontSize: '130%',
                          }}
                        >
                          {parser.name}
                        </li>
                      )}
                      <li onClick={sourcesClickHandler}>Sources</li>
                      <li onClick={queuesClickHandler}>Queues</li>
                      <li onClick={preprocessingsClickHandler}>
                        Pre-processings
                      </li>
                      <li onClick={ocrClickHandler}>OCR</li>
                      {parser.type == 'LAYOUT' && (
                        <li onClick={aiChatClickHandler}>AI Chat</li>
                      )}
                      <li onClick={splittingClickHandler}>Splitting</li>
                      <li onClick={fieldsClickHandler}>Fields</li>
                      {parser.type == 'LAYOUT' && (
                        <li onClick={postprocessingsClickHandler}>
                          Post-processings
                        </li>
                      )}
                      {parser.type == 'LAYOUT' && (
                        <li onClick={integrationsClickHandler}>Integrations</li>
                      )}
                      <li onClick={statisticsClickHandler}>Statistics</li>
                      <li onClick={settingsClickHandler}>Settings</li>
                    </ul>
                  </div>
                </div>
                <div
                  className="col-12 col-md-10 flex-grow-1"
                  style={{
                    paddingLeft: 0,
                    paddingRight: 0,
                    paddingBottom: 10,
                    minHeight: '480px',
                    display: 'flex',
                    width: 'calc(100% - 200px)',
                  }}
                >
                  {children}
                </div>
              </div>
            </div>
          </main>
          <footer className={adminStyles.footer}>
            <div style={{ width: '100%', padding: '0 10px' }}>
              <div className="row" style={{ padding: '0 10px' }}>
                <div className="col-sm" style={{ padding: '10px' }}>
                  <div className={adminStyles.copyright}>
                    2023. All rights reserved.
                  </div>
                </div>
              </div>
            </div>
          </footer>
        </div>
      )}
    </>
  )
}
