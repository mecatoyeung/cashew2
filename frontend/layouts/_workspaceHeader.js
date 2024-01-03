import Head from "next/head"
import Image from "next/image"
import Link from "next/link"

import { useRouter } from "next/router"
import { useState, useEffect } from "react"

import { Nav } from "react-bootstrap"
import { Button } from "react-bootstrap"
import Dropdown from 'react-bootstrap/Dropdown'
import DropdownButton from 'react-bootstrap/DropdownButton'

import service from "../service"

import headerStyles from "../styles/WorkspaceHeader.module.css"

export default function WorkspaceHeader({ children }) {
  const router = useRouter()

  let { parserId } = router.query

  const [parser, setParser] = useState(null)

  const [userProfile, setUserProfile] = useState(null)

  const getParser = () => {
    if (!parserId) return
    service.get("parsers/" + parserId + "/", (response) => {
      setParser(response.data)
    })
  }

  const getUserProfile = () => {
    service.get("profiles/", (response) => {
      setUserProfile(response.data[0])
    })
  }

  const logoutBtnClickHandler = () => {
    service.post("rest-auth/logout/", {}, () => {
      localStorage.removeItem("token")
      router.push("/")
    })
  }

  useEffect(() => {
    getUserProfile()
  }, [])

  useEffect(() => {
    getParser()
  }, [parserId])

  return (
    <header className={headerStyles.header}>
        <div>
            <div className="row" style={{ padding: 0, margin: 0 }}>
                <div
                className="col-6 col-md-6"
                style={{ paddingLeft: 20, paddingRight: 0 }}
                >
                <div className={headerStyles.logoDiv}>
                    <Image
                    src="/static/img/logo.png"
                    width="40"
                    height="36"
                    alt="Cashew Docparser"
                    />
                </div>
                <h2>Cashew</h2>
                &nbsp;&nbsp;&nbsp;
                <Nav.Link
                    href="/workspace/parsers"
                    style={{ display: "inline-block", verticalAlign: "top" }}
                >
                    <i
                    className={
                        headerStyles.parsersIcon + " bi bi-grid"
                    }
                    ></i>
                </Nav.Link>
                </div>
                <div
                className="col-6 col-md-6"
                style={{ paddingLeft: 0, paddingRight: 20 }}
                >
                <nav className={headerStyles.nav}>
                    <ul>
                    <li>
                        <DropdownButton id="dropdown-basic-button" title="Account">
                        {userProfile && (
                            <Dropdown.Item href="#">Welcome, {userProfile.fullName}</Dropdown.Item>
                        )}
                        <Dropdown.Item href="/account/profile">Profile</Dropdown.Item>
                        <Dropdown.Item href="/account/change-password">Change Password</Dropdown.Item>
                        <Dropdown.Item href="#" onClick={logoutBtnClickHandler}>Logout</Dropdown.Item>
                        </DropdownButton>
                    </li>
                    </ul>
                </nav>
                </div>
            </div>
        </div>
    </header>
    );
}
