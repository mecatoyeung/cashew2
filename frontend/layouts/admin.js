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
                      <Link href={'/admin/parsers/' + parserId + '/sources'}>
                        <li>Sources</li>
                      </Link>
                      <Link href={'/admin/parsers/' + parserId + '/queues'}>
                        <li>Queues</li>
                      </Link>
                      <Link
                        href={'/admin/parsers/' + parserId + '/preprocessings'}
                      >
                        <li>Pre-processings</li>
                      </Link>
                      <Link href={'/admin/parsers/' + parserId + '/ocr'}>
                        <li>OCR</li>
                      </Link>
                      {parser.type == 'LAYOUT' && (
                        <Link href={'/admin/parsers/' + parserId + '/aichat'}>
                          <li>AI Chat</li>
                        </Link>
                      )}
                      <Link href={'/admin/parsers/' + parserId + '/splitting'}>
                        <li>Splitting</li>
                      </Link>
                      <Link href={'/admin/parsers/' + parserId + '/rules'}>
                        <li>Fields</li>
                      </Link>
                      {parser.type == 'LAYOUT' && (
                        <Link
                          href={
                            '/admin/parsers/' + parserId + '/postprocessings'
                          }
                        >
                          <li>Post-processings</li>
                        </Link>
                      )}
                      {parser.type == 'LAYOUT' && (
                        <Link
                          href={'/admin/parsers/' + parserId + '/integrations'}
                        >
                          <li>Integrations</li>
                        </Link>
                      )}
                      <Link href={'/admin/parsers/' + parserId + '/statistics'}>
                        <li>Statistics</li>
                      </Link>
                      <Link href={'/admin/parsers/' + parserId + '/settings'}>
                        <li>Settings</li>
                      </Link>
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
