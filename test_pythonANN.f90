!compile w/ shared library: 'gfortran -o run_test -L ./pythonANN/ -lplugin test_pythonANN.f90'

PROGRAM COUPLING_TEST
   use, intrinsic :: iso_c_binding
   implicit none
   interface
      subroutine get_rates(x1, x2, x3, x4, x5, n, y1, y2, b) bind (c)
         use iso_c_binding
         real*8                        :: x1
         real*8                        :: x2
         real*8                        :: x3
         integer(c_int)                :: n
         real*8                        :: x4(n)
         real*8                        :: x5(n)
         real*8                        :: y1
         real*8                        :: y2
         integer(c_int)                :: b
      end subroutine get_rates
   end interface

   !DECLARE INPUT PARAMETERS
   real*8                              :: T_gas
   real*8                              :: nH
   real*8                              :: n_H

   real*8, allocatable                 :: l(:)
   integer                             :: l_count
   real*8, allocatable                 :: u(:)
   integer                             :: u_count

   !DECLARE OUPUTS
   real*8                              :: LH
   real*8                              :: ER

   !LOOPING AND TIMING
   integer                             :: i
   integer                             :: ANNcount = 0
   real*8                              :: time1
   real*8                              :: time2

   !writing checkpoints
   CHARACTER(200)                      :: modele        = 'simX'    ! Root name of output files
   INTEGER                             :: b_checkpoints             ! boolean int: do we save ANN chechpoints (0 or 1)


   !ASSIGN INPUT VALUES (sample 1 of testT01)
   T_gas = 4.113083490000000353e+01
   nH = 1.194153369999999995e+05
   n_H = 1.000000000000000000e+08

   !read in lambda from test file
	open (unit=1, file='./pythonANN/test_data/lam_test.txt', status='old', action='read')

		read(1,*) l_count
		allocate (l(l_count))

        read(1,*) l

	close(1)

   !read in u from test file
   	open (unit=1, file='./pythonANN/test_data/u_test.txt', status='old', action='read')

		read(1,*) u_count
		allocate (u(u_count))

        read(1,*) u

	close(1)


   !!!! ACTION !!!!
   b_checkpoints = 0
   DO i=1,100
       CALL CPU_TIME(time1)
       call get_rates(T_gas, nH, n_H, l, u, size(u), LH, ER, b_checkpoints)
       CALL CPU_TIME(time2)
       ANNcount = ANNcount+1
       WRITE(*,'(A11,ES10.3,A6,I4)') 'ANN call : ', time2 - time1, 's - no', ANNcount
       PRINT *, LH
       PRINT *, ER
   END DO


   !DESIRED OUTPUT:
   ! LH 4.454582101342124460e-18
   ! ER 1.761998920326483102e-19

END PROGRAM COUPLING_TEST



