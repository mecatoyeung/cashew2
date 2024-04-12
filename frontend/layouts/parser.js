import Head from 'next/head'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { useState, useEffect } from 'react'

import { Button } from 'react-bootstrap'
import Dropdown from 'react-bootstrap/Dropdown'
import DropdownButton from 'react-bootstrap/DropdownButton'

import service from '../service'

import hasPermission from '../helpers/hasPermission'

import adminLayoutStyles from '../styles/AdminLayout.module.css'
import axios from 'axios'

export default function ParserLayout({ children }) {
  const router = useRouter()

  const [user, setUser] = useState(null)

  const getUser = () => {
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
    getUser()
  }, [])

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
      <div className={adminLayoutStyles.wrapper}>
        <header className={adminLayoutStyles.header}>
          <div className="container-md">
            <div className="row">
              <div className="col-4 col-md-4">
                <div className={adminLayoutStyles.logoDiv}>
                  <Link
                    href={
                      router.pathname.split('/')[1] == 'admin'
                        ? '/admin/parsers'
                        : '/workbench/parsers'
                    }
                  >
                    <img
                      src="/static/img/logo.png"
                      width="40"
                      height="36"
                      alt="Cashew Docparser"
                    />
                  </Link>
                </div>
                <Link
                  href={
                    router.pathname.split('/')[1] == 'admin'
                      ? '/admin/parsers'
                      : '/workbench/parsers'
                  }
                >
                  <h2>Cashew</h2>
                </Link>
                <a
                  href="#"
                  onClick={() => router.back()}
                  style={{
                    display: 'inline-block',
                    verticalAlign: 'top',
                    marginRight: 10,
                  }}
                >
                  <i
                    className={
                      adminLayoutStyles.parsersIcon + ' bi bi-arrow-90deg-left'
                    }
                  ></i>
                </a>
              </div>
              <div className="col-8 col-md-8">
                <nav className={adminLayoutStyles.nav}>
                  <ul>
                    <li>
                      <DropdownButton
                        id="dropdown-basic-button"
                        title="Account"
                      >
                        {user && (
                          <Dropdown.Item href="#">
                            Welcome, {user.profile.fullName}
                          </Dropdown.Item>
                        )}
                        {router.pathname.split('/')[1] == 'admin' && (
                          <Dropdown.Item href="/workbench/parsers">
                            Switch to Workbench
                          </Dropdown.Item>
                        )}
                        {router.pathname.split('/')[1] == 'workbench' &&
                          hasPermission('cashew_parser_management') && (
                            <Dropdown.Item href="/admin/parsers">
                              Switch to Admin Console
                            </Dropdown.Item>
                          )}
                        <Dropdown.Item href="/account/profile">
                          Account
                        </Dropdown.Item>
                        {hasPermission('cashew_user_management') && (
                          <Dropdown.Item href="/settings/users">
                            User Management
                          </Dropdown.Item>
                        )}
                        <Dropdown.Item href="#" onClick={logoutBtnClickHandler}>
                          Logout
                        </Dropdown.Item>
                      </DropdownButton>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </header>
        <hr className={adminLayoutStyles.headerHr} />
        <main className={adminLayoutStyles.main + ' d-flex flex-column'}>
          <div
            className={
              adminLayoutStyles.sideNavContainerDiv +
              ' container-md d-flex flex-grow-1'
            }
          >
            <div className="row d-flex flex-grow-1">
              <div
                className="col-12"
                style={{ paddingLeft: 0, paddingRight: 0 }}
              >
                {children}
              </div>
            </div>
          </div>
        </main>
        <footer className={adminLayoutStyles.footer}>
          <div className="container">
            <div className="row">
              <div className="col-sm">
                <div className={adminLayoutStyles.copyright}>
                  2023. All rights reserved.
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  )
}
