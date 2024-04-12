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

import settingsStyles from '../styles/Settings.module.css'

import hasPermission from '../helpers/hasPermission'

export default function AccountLayout({ children }) {
  const router = useRouter()

  let {} = router.query

  useEffect(() => {
    if (!hasPermission('cashew_user_management')) {
      router.push('/workbench/parsers')
    }
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
      {hasPermission('cashew_user_management') && (
        <div className={settingsStyles.wrapper}>
          <AdminHeader />
          <hr className={settingsStyles.headerHr} />
          <main className={settingsStyles.main + ' d-flex flex-column'}>
            <div
              className={
                settingsStyles.sideNavContainerDiv + ' d-flex flex-grow-1'
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
                    className={
                      settingsStyles.sideNavDiv + ' d-flex flex-grow-1'
                    }
                  >
                    <ul className={settingsStyles.sideNavUl}>
                      <Link href={'/settings/users'}>
                        <li>Users</li>
                      </Link>
                      <Link href={'/settings/groups'}>
                        <li>User Groups</li>
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
                    flexDirection: 'column',
                    width: 'calc(100% - 200px)',
                  }}
                >
                  {children}
                </div>
              </div>
            </div>
          </main>
          <footer className={settingsStyles.footer}>
            <div style={{ width: '100%', padding: '0 10px' }}>
              <div className="row" style={{ padding: '0 10px' }}>
                <div className="col-sm" style={{ padding: '10px' }}>
                  <div className={settingsStyles.copyright}>
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
